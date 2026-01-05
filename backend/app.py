from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
import tensorflow as tf
import os
import json
from mediapipe.python.solutions import pose as mp_pose
import re

def normalize_pose_name(name):
    name = re.sub(r'[_\-]+', ' ', name)
    name = name.strip(" _-")
    return name.title()

app = Flask(__name__)
CORS(app)
pose_detector = mp_pose.Pose(static_image_mode=True)
model = tf.keras.models.load_model('yoga_pose_model.h5')

with open('processed_data/yoga_pose_model_labels.json', 'r') as f:
    raw_class_names = json.load(f)['classes']
    class_names = [normalize_pose_name(p) for p in raw_class_names]

# Comprehensive pose feedback database
pose_feedback = {
    normalize_pose_name("Akarna_Dhanurasana"): {
        "description": "Archer Pose - A challenging seated pose that combines flexibility and balance.",
        "alignment_cues": [
            "Sit tall with legs extended",
            "Grab big toe of one foot with opposite hand",
            "Draw the foot up and back like pulling a bow",
            "Keep spine straight and chest open"
        ],
        "benefits": [
            "Improves hip flexibility",
            "Strengthens core muscles",
            "Enhances balance and concentration",
            "Stretches hamstrings and shoulders"
        ],
        "common_mistakes": [
            "Rounding the back",
            "Forcing the stretch too aggressively",
            "Neglecting the supporting leg",
            "Holding breath during the pose"
        ],
        "modifications": "Use a strap around the foot if you can't reach it directly",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Bharadvajas_Twist_pose_or_Bharadvajasana_I_"): {
        "description": "A gentle seated spinal twist named after the sage Bharadvaja.",
        "alignment_cues": [
            "Sit with legs to one side in a Z-shape",
            "Place one hand behind you for support",
            "Twist from the base of the spine upward",
            "Keep both sitting bones grounded"
        ],
        "benefits": [
            "Improves spinal mobility",
            "Aids digestion",
            "Relieves back tension",
            "Calms the nervous system"
        ],
        "common_mistakes": [
            "Twisting only from the neck",
            "Lifting the sitting bones",
            "Forcing the twist",
            "Collapsing through the spine"
        ],
        "modifications": "Sit on a blanket or cushion for comfort",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Boat_Pose_or_Paripurna_Navasana_"): {
        "description": "Navasana - A core-strengthening pose that resembles a boat.",
        "alignment_cues": [
            "Balance on sitting bones with knees bent",
            "Lift chest and straighten spine",
            "Extend legs to create a V-shape",
            "Reach arms forward parallel to floor"
        ],
        "benefits": [
            "Strengthens core muscles",
            "Improves balance and stability",
            "Tones abdominal organs",
            "Builds mental focus"
        ],
        "common_mistakes": [
            "Rounding the back",
            "Holding breath",
            "Gripping toes too tightly",
            "Tensing shoulders"
        ],
        "modifications": "Keep knees bent or hold behind thighs for support",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Bound_Angle_Pose_or_Baddha_Konasana_"): {
        "description": "Baddha Konasana - A seated hip opener that resembles a butterfly.",
        "alignment_cues": [
            "Sit with soles of feet together",
            "Hold feet or ankles gently",
            "Lengthen spine before folding forward",
            "Keep knees relaxed"
        ],
        "benefits": [
            "Opens hips and groins",
            "Stretches inner thighs",
            "Calms the mind",
            "Stimulates reproductive organs"
        ],
        "common_mistakes": [
            "Forcing knees down",
            "Rounding spine excessively",
            "Pulling feet too close",
            "Bouncing to deepen stretch"
        ],
        "modifications": "Sit on a cushion or place blocks under knees for support",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Bow_Pose_or_Dhanurasana_"): {
        "description": "Dhanurasana - A backbend that resembles an archer's bow.",
        "alignment_cues": [
            "Lie on belly and bend knees",
            "Reach back to grab ankles",
            "Lift chest and thighs simultaneously",
            "Keep knees hip-width apart"
        ],
        "benefits": [
            "Strengthens back muscles",
            "Opens chest and shoulders",
            "Improves posture",
            "Stimulates digestive organs"
        ],
        "common_mistakes": [
            "Kicking feet into hands forcefully",
            "Widening knees too much",
            "Straining the neck",
            "Not engaging the back muscles"
        ],
        "modifications": "Use a strap around ankles if you can't reach them",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Bridge_Pose_or_Setu_Bandha_Sarvangasana_"): {
        "description": "Setu Bandhasana - A gentle backbend that opens the heart.",
        "alignment_cues": [
            "Lie on back with knees bent",
            "Press feet down and lift hips",
            "Keep knees parallel and hip-width apart",
            "Clasp hands under back if comfortable"
        ],
        "benefits": [
            "Strengthens glutes and hamstrings",
            "Opens chest and hip flexors",
            "Calms the brain",
            "Improves circulation"
        ],
        "common_mistakes": [
            "Letting knees splay out",
            "Overarching lower back",
            "Turning head while in pose",
            "Not engaging glutes"
        ],
        "modifications": "Place a block between thighs or use a bolster under sacrum",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Camel_Pose_or_Ustrasana_"): {
        "description": "Ustrasana - A deep heart-opening backbend.",
        "alignment_cues": [
            "Kneel with shins parallel",
            "Place hands on lower back",
            "Lift chest and reach for heels",
            "Keep hips moving forward"
        ],
        "benefits": [
            "Opens entire front body",
            "Strengthens back muscles",
            "Improves posture",
            "Energizes the body"
        ],
        "common_mistakes": [
            "Dropping head back too quickly",
            "Collapsing into lower back",
            "Not warming up sufficiently",
            "Forcing the pose"
        ],
        "modifications": "Keep hands on lower back or use blocks on calves",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Cat_Cow_Pose_or_Marjaryasana_"): {
        "description": "Marjaryasana-Bitilasana - A gentle spinal warm-up sequence.",
        "alignment_cues": [
            "Start in tabletop position",
            "Arch back and lift chest for Cow",
            "Round spine and tuck chin for Cat",
            "Move slowly with breath"
        ],
        "benefits": [
            "Mobilizes the spine",
            "Relieves back tension",
            "Improves posture",
            "Connects breath with movement"
        ],
        "common_mistakes": [
            "Moving too quickly",
            "Not engaging core",
            "Overextending neck",
            "Ignoring breath coordination"
        ],
        "modifications": "Place cushion under knees for comfort",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Chair_Pose_or_Utkatasana_"): {
        "description": "Utkatasana - A powerful standing pose that builds strength and endurance.",
        "alignment_cues": [
            "Stand with feet hip-width apart",
            "Bend knees as if sitting in a chair",
            "Reach arms overhead",
            "Keep weight in heels"
        ],
        "benefits": [
            "Strengthens thighs and glutes",
            "Builds core stability",
            "Improves balance",
            "Generates heat in the body"
        ],
        "common_mistakes": [
            "Knees caving inward",
            "Weight shifting to toes",
            "Arching back excessively",
            "Shoulders creeping toward ears"
        ],
        "modifications": "Sit back against a wall or keep hands on hips",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Child_Pose_or_Balasana_"): {
        "description": "Balasana - A restful pose that provides comfort and introspection.",
        "alignment_cues": [
            "Kneel and sit back on heels",
            "Fold forward with arms extended",
            "Rest forehead on the floor",
            "Allow hips to sink toward heels"
        ],
        "benefits": [
            "Calms the nervous system",
            "Gently stretches hips and back",
            "Relieves stress and anxiety",
            "Aids digestion"
        ],
        "common_mistakes": [
            "Sitting too far from heels",
            "Forcing forehead to floor",
            "Tensing shoulders",
            "Holding too much weight in arms"
        ],
        "modifications": "Place pillow between calves and thighs, or under forehead",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Cobra_Pose_or_Bhujangasana_"): {
        "description": "Bhujangasana - A gentle backbend that strengthens the spine.",
        "alignment_cues": [
            "Lie on belly with palms under shoulders",
            "Press pubic bone down",
            "Lift chest using back muscles",
            "Keep shoulders away from ears"
        ],
        "benefits": [
            "Strengthens spine and arms",
            "Opens chest and lungs",
            "Stimulates abdominal organs",
            "Improves mood"
        ],
        "common_mistakes": [
            "Pushing too hard with hands",
            "Lifting too high too soon",
            "Hunching shoulders",
            "Not engaging leg muscles"
        ],
        "modifications": "Keep forearms on floor or place cushion under hips",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Cockerel_Pose"): {
        "description": "Kukkutasana - An arm balance that requires strength and focus.",
        "alignment_cues": [
            "Start in Lotus pose",
            "Thread arms through legs",
            "Press palms down and lift body",
            "Keep elbows close to body"
        ],
        "benefits": [
            "Strengthens arms and wrists",
            "Improves balance and concentration",
            "Builds core strength",
            "Challenges mental focus"
        ],
        "common_mistakes": [
            "Not preparing wrists adequately",
            "Attempting without proper hip flexibility",
            "Collapsing through chest",
            "Holding breath"
        ],
        "modifications": "Practice arm positioning without lifting first",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Corpse_Pose_or_Savasana_"): {
        "description": "Savasana - The final relaxation pose that integrates the practice.",
        "alignment_cues": [
            "Lie flat on back with limbs relaxed",
            "Allow feet to fall naturally apart",
            "Rest arms slightly away from body",
            "Close eyes and soften facial muscles"
        ],
        "benefits": [
            "Reduces stress and anxiety",
            "Lowers blood pressure",
            "Improves sleep quality",
            "Allows body to integrate practice"
        ],
        "common_mistakes": [
            "Fidgeting or adjusting constantly",
            "Thinking it's 'just lying down'",
            "Not allowing enough time",
            "Forcing relaxation"
        ],
        "modifications": "Use bolster under knees or blanket for warmth",
        "difficulty": "Beginner (but challenging to master)"
    },
    
    normalize_pose_name("Cow_Face_Pose_or_Gomukhasana_"): {
        "description": "Gomukhasana - A seated pose that stretches shoulders and hips simultaneously.",
        "alignment_cues": [
            "Sit with legs stacked, knees aligned",
            "Reach one arm up and back",
            "Bring other arm up from below to clasp hands",
            "Keep spine straight"
        ],
        "benefits": [
            "Stretches shoulders and hips",
            "Improves posture",
            "Releases tension in arms",
            "Calms the mind"
        ],
        "common_mistakes": [
            "Leaning to one side",
            "Forcing hands to touch",
            "Hunching shoulders",
            "Not sitting evenly on both sitting bones"
        ],
        "modifications": "Use a strap between hands or sit on a cushion",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Crane_(Crow)_Pose_or_Bakasana_"): {
        "description": "Bakasana - An arm balance that builds strength and confidence.",
        "alignment_cues": [
            "Squat with hands on floor",
            "Rest knees on upper arms",
            "Shift weight forward onto hands",
            "Lift toes and find balance point"
        ],
        "benefits": [
            "Strengthens arms and core",
            "Improves balance and focus",
            "Builds confidence",
            "Tones abdominal organs"
        ],
        "common_mistakes": [
            "Placing knees too low on arms",
            "Not shifting weight forward enough",
            "Gripping mat with fingertips",
            "Looking down instead of forward"
        ],
        "modifications": "Place block under forehead or practice on higher surface",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Dolphin_Plank_Pose_or_Makara_Adho_Mukha_Svanasana_"): {
        "description": "A challenging variation of plank pose on forearms.",
        "alignment_cues": [
            "Start in forearm plank position",
            "Keep forearms parallel",
            "Engage core and maintain straight line",
            "Press forearms down actively"
        ],
        "benefits": [
            "Strengthens core and arms",
            "Builds shoulder stability",
            "Improves posture",
            "Prepares for advanced arm balances"
        ],
        "common_mistakes": [
            "Sagging hips",
            "Pike position (hips too high)",
            "Not engaging leg muscles",
            "Holding breath"
        ],
        "modifications": "Drop knees to floor or shorten hold time",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Dolphin_Pose_or_Ardha_Pincha_Mayurasana_"): {
        "description": "Ardha Pincha Mayurasana - A preparation for forearm stand.",
        "alignment_cues": [
            "Start on forearms and knees",
            "Tuck toes and lift hips up",
            "Walk feet closer to elbows",
            "Keep forearms parallel"
        ],
        "benefits": [
            "Strengthens shoulders and arms",
            "Stretches hamstrings and calves",
            "Improves circulation",
            "Prepares for inversions"
        ],
        "common_mistakes": [
            "Widening elbows",
            "Collapsing through shoulders",
            "Not engaging leg muscles",
            "Turning head to look around"
        ],
        "modifications": "Use blocks between hands or practice against wall",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Downward-Facing_Dog_pose_or_Adho_Mukha_Svanasana_"): {
        "description": "Adho Mukha Svanasana - A foundational pose that appears in most sequences.",
        "alignment_cues": [
            "Start on hands and knees",
            "Tuck toes and lift hips up and back",
            "Straighten arms and legs",
            "Create inverted V-shape"
        ],
        "benefits": [
            "Strengthens arms and legs",
            "Stretches hamstrings and calves",
            "Calms the mind",
            "Energizes the body"
        ],
        "common_mistakes": [
            "Weight too far forward in hands",
            "Hunching shoulders",
            "Not engaging leg muscles",
            "Forcing heels to floor"
        ],
        "modifications": "Pedal feet, bend knees, or use blocks under hands",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Eagle_Pose_or_Garudasana_"): {
        "description": "Garudasana - A balancing pose that wraps arms and legs.",
        "alignment_cues": [
            "Stand and wrap one leg around the other",
            "Cross arms and wrap them around each other",
            "Sit back slightly and find balance",
            "Keep lifted leg's toe on floor for stability"
        ],
        "benefits": [
            "Improves balance and concentration",
            "Strengthens legs and core",
            "Stretches shoulders and upper back",
            "Relieves tension in shoulders"
        ],
        "common_mistakes": [
            "Leaning too far forward",
            "Not wrapping limbs properly",
            "Holding breath",
            "Gripping with wrapped leg too tightly"
        ],
        "modifications": "Use wall for support or keep toe of wrapped leg on floor",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Eight-Angle_Pose_or_Astavakrasana_"): {
        "description": "Astavakrasana - An advanced arm balance named after the sage Ashtavakra.",
        "alignment_cues": [
            "Start seated with one leg over arm",
            "Hook ankles together to one side",
            "Press hands down and lift body",
            "Extend legs to one side"
        ],
        "benefits": [
            "Strengthens arms and core",
            "Improves balance and focus",
            "Builds mental concentration",
            "Challenges physical limits"
        ],
        "common_mistakes": [
            "Not hooking legs properly",
            "Insufficient warm-up",
            "Collapsing through chest",
            "Attempting without adequate strength"
        ],
        "modifications": "Practice the arm position without lifting first",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Extended_Puppy_Pose_or_Uttana_Shishosana_"): {
        "description": "Uttana Shishosana - A heart-opening pose that combines child's pose with backbend.",
        "alignment_cues": [
            "Start in tabletop position",
            "Walk hands forward and lower chest",
            "Keep hips over knees",
            "Rest forehead or chin on floor"
        ],
        "benefits": [
            "Opens chest and shoulders",
            "Gently stretches spine",
            "Calms the mind",
            "Relieves stress and tension"
        ],
        "common_mistakes": [
            "Moving hips forward",
            "Forcing chest to floor",
            "Not supporting with arms",
            "Tensing shoulders"
        ],
        "modifications": "Place cushion under forehead or chest",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Extended_Revolved_Side_Angle_Pose_or_Utthita_Parsvakonasana_"): {
        "description": "Parivrtta Utthita Parsvakonasana - A deep twisting variation of side angle pose.",
        "alignment_cues": [
            "Start in side angle pose",
            "Bring opposite elbow to outside of front thigh",
            "Twist from base of spine",
            "Extend top arm over ear"
        ],
        "benefits": [
            "Deeply twists the spine",
            "Strengthens legs and core",
            "Improves balance",
            "Stimulates digestive organs"
        ],
        "common_mistakes": [
            "Twisting only from neck",
            "Collapsing over front leg",
            "Not keeping back leg strong",
            "Forcing the twist"
        ],
        "modifications": "Keep top hand on hip or use block under bottom hand",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Extended_Revolved_Triangle_Pose_or_Utthita_Trikonasana_"): {
        "description": "Parivrtta Utthita Trikonasana - A challenging twisted standing pose.",
        "alignment_cues": [
            "Stand in wide-legged forward fold",
            "Turn one foot out 90 degrees",
            "Place opposite hand on floor or block",
            "Twist spine and reach other arm up"
        ],
        "benefits": [
            "Deeply twists the spine",
            "Stretches hamstrings and hips",
            "Improves balance and focus",
            "Strengthens legs and core"
        ],
        "common_mistakes": [
            "Rounding the back",
            "Not keeping legs strong",
            "Forcing hand to floor",
            "Twisting only from shoulders"
        ],
        "modifications": "Use block under hand or keep hand on shin",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Feathered_Peacock_Pose_or_Pincha_Mayurasana_"): {
        "description": "Pincha Mayurasana - An advanced inversion that requires strength and balance.",
        "alignment_cues": [
            "Start in dolphin pose at wall",
            "Keep forearms parallel",
            "Kick up one leg at a time",
            "Find balance point and straighten legs"
        ],
        "benefits": [
            "Strengthens shoulders and arms",
            "Improves balance and focus",
            "Increases circulation",
            "Builds confidence"
        ],
        "common_mistakes": [
            "Widening elbows",
            "Not warming up adequately",
            "Kicking up too aggressively",
            "Collapsing through shoulders"
        ],
        "modifications": "Practice against wall or with partner assistance",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Firefly_Pose_or_Tittibhasana_"): {
        "description": "Tittibhasana - An arm balance that requires hip flexibility and arm strength.",
        "alignment_cues": [
            "Start in deep squat",
            "Place hands behind legs on floor",
            "Shift weight to hands and lift legs",
            "Straighten legs as much as possible"
        ],
        "benefits": [
            "Strengthens arms and core",
            "Opens hips and hamstrings",
            "Improves balance",
            "Builds mental focus"
        ],
        "common_mistakes": [
            "Not getting legs high enough on arms",
            "Insufficient hip opening preparation",
            "Collapsing through chest",
            "Not engaging core"
        ],
        "modifications": "Keep feet on floor or use blocks for height",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Fish_Pose_or_Matsyasana_"): {
        "description": "Matsyasana - A heart-opening backbend that opens the throat.",
        "alignment_cues": [
            "Lie on back with legs straight",
            "Place hands under lower back",
            "Press elbows down and lift chest",
            "Crown of head touches floor lightly"
        ],
        "benefits": [
            "Opens chest and throat",
            "Counteracts forward head posture",
            "Stimulates thyroid gland",
            "Relieves tension in neck and shoulders"
        ],
        "common_mistakes": [
            "Too much weight on head",
            "Forcing the backbend",
            "Not supporting with arms",
            "Tensing jaw and face"
        ],
        "modifications": "Use bolster under back or keep head lifted",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Four-Limbed_Staff_Pose_or_Chaturanga_Dandasana_"): {
        "description": "Chaturanga Dandasana - A strength-building pose fundamental to vinyasa sequences.",
        "alignment_cues": [
            "Start in plank pose",
            "Lower body as one unit",
            "Keep elbows close to ribs",
            "Stop when elbows are at 90 degrees"
        ],
        "benefits": [
            "Strengthens arms, core, and legs",
            "Builds functional strength",
            "Improves posture",
            "Prepares for arm balances"
        ],
        "common_mistakes": [
            "Elbows flaring out wide",
            "Sinking too low",
            "Collapsing through core",
            "Not keeping legs active"
        ],
        "modifications": "Lower knees to floor or use block under chest",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Frog_Pose_or_Bhekasana"): {
        "description": "Bhekasana - A deep hip opener that stretches the groins and inner thighs.",
        "alignment_cues": [
            "Start on hands and knees",
            "Widen knees as far as comfortable",
            "Keep shins parallel to each other",
            "Lower to forearms if accessible"
        ],
        "benefits": [
            "Opens hips and groins deeply",
            "Stretches inner thigh muscles",
            "Relieves lower back tension",
            "Calms the nervous system"
        ],
        "common_mistakes": [
            "Forcing knees too wide",
            "Not keeping feet flexed",
            "Collapsing through core",
            "Ignoring pain signals"
        ],
        "modifications": "Place cushions under knees or stay on hands",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Garland_Pose_or_Malasana_"): {
        "description": "Malasana - A deep squat that is natural and grounding.",
        "alignment_cues": [
            "Squat with feet slightly wider than hips",
            "Keep heels down if possible",
            "Bring palms together at heart center",
            "Use elbows to gently widen knees"
        ],
        "benefits": [
            "Opens hips and groins",
            "Strengthens legs and core",
            "Aids digestion",
            "Grounds and centers the mind"
        ],
        "common_mistakes": [
            "Forcing heels down",
            "Collapsing forward",
            "Not engaging core",
            "Putting too much pressure on knees"
        ],
        "modifications": "Sit on block or blanket, or place blanket under heels",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Gate_Pose_or_Parighasana_"): {
        "description": "Parighasana - A kneeling side stretch that opens the side body.",
        "alignment_cues": [
            "Kneel and extend one leg to the side",
            "Keep extended leg straight with foot flat",
            "Side bend over extended leg",
            "Reach top arm over ear"
        ],
        "benefits": [
            "Stretches side body and spine",
            "Opens intercostal muscles",
            "Improves breathing capacity",
            "Releases tension in torso"
        ],
        "common_mistakes": [
            "Collapsing forward",
            "Not keeping extended leg straight",
            "Forcing the side bend",
            "Neglecting the supporting side"
        ],
        "modifications": "Place hand on shin instead of floor or use block",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Half_Lord_of_the_Fishes_Pose_or_Ardha_Matsyendrasana_"): {
        "description": "Ardha Matsyendrasana - A seated spinal twist with many variations.",
        "alignment_cues": [
            "Sit with one leg straight, other foot outside opposite thigh",
            "Hug bent knee or place elbow against it",
            "Twist from base of spine",
            "Keep both sitting bones grounded"
        ],
        "benefits": [
            "Improves spinal mobility",
            "Aids digestion and detoxification",
            "Strengthens obliques",
            "Relieves back tension"
        ],
        "common_mistakes": [
            "Twisting only from neck",
            "Lifting sitting bones",
            "Forcing the twist",
            "Not lengthening spine first"
        ],
        "modifications": "Sit on cushion or keep bottom leg straight",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Half_Moon_Pose_or_Ardha_Chandrasana_"): {
        "description": "Ardha Chandrasana - A challenging balance pose that strengthens and opens.",
        "alignment_cues": [
            "From triangle pose, shift weight to front leg",
            "Place hand on floor in front of front foot",
            "Lift back leg parallel to floor",
            "Open chest and reach top arm up"
        ],
        "benefits": [
            "Improves balance and coordination",
            "Strengthens legs and core",
            "Opens hips and chest",
            "Builds mental focus"
        ],
        "common_mistakes": [
            "Putting too much weight on bottom hand",
            "Not keeping standing leg strong",
            "Lifting leg too high",
            "Collapsing through torso"
        ],
        "modifications": "Use block under hand or practice against wall",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Handstand_pose_or_Adho_Mukha_Vrksasana_"): {
        "description": "Adho Mukha Vrksasana - The king of arm balances requiring strength and balance.",
        "alignment_cues": [
            "Start in downward dog facing wall",
            "Walk feet closer to hands",
            "Kick up one leg at a time",
            "Engage entire body and breathe"
        ],
        "benefits": [
            "Strengthens arms, shoulders, and core",
            "Improves circulation and lymphatic drainage",
            "Builds confidence and mental focus",
            "Energizes the entire body"
        ],
        "common_mistakes": [
            "Not warming up adequately",
            "Kicking up too aggressively",
            "Collapsing through shoulders",
            "Holding breath"
        ],
        "modifications": "Practice against wall or with partner assistance",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Happy_Baby_Pose_or_Ananda_Balasana_"): {
        "description": "Ananda Balasana - A playful hip opener that releases the lower back.",
        "alignment_cues": [
            "Lie on back and hug knees to chest",
            "Grab outsides of feet with hands",
            "Draw knees toward armpits",
            "Keep sacrum grounded"
        ],
        "benefits": [
            "Opens hips and groins",
            "Releases lower back tension",
            "Calms the nervous system",
            "Brings playfulness to practice"
        ],
        "common_mistakes": [
            "Lifting sacrum off floor",
            "Forcing knees too wide",
            "Tensing shoulders",
            "Not breathing deeply"
        ],
        "modifications": "Hold behind thighs instead of feet or use strap",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Head-to-Knee_Forward_Bend_pose_or_Janu_Sirsasana_"): {
        "description": "Janu Sirsasana - A seated forward fold with a twist element.",
        "alignment_cues": [
            "Sit with one leg straight, bend other knee out to side",
            "Square hips toward straight leg",
            "Fold forward over straight leg",
            "Keep spine long as you fold"
        ],
        "benefits": [
            "Stretches hamstrings and spine",
            "Calms the mind",
            "Stimulates digestive organs",
            "Relieves stress and fatigue"
        ],
        "common_mistakes": [
            "Rounding spine immediately",
            "Not squaring hips",
            "Forcing forehead to knee",
            "Holding breath"
        ],
        "modifications": "Sit on cushion or use strap around foot",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Heron_Pose_or_Krounchasana_"): {
        "description": "Krounchasana - A seated pose that combines hip opening with hamstring stretch.",
        "alignment_cues": [
            "Sit with one leg in hero pose, other leg straight",
            "Hold straight leg with both hands",
            "Draw leg toward torso",
            "Keep spine straight and chest open"
        ],
        "benefits": [
            "Stretches hamstrings and calves deeply",
            "Opens hip flexors",
            "Improves posture",
            "Builds core strength"
        ],
        "common_mistakes": [
            "Forcing leg straight if tight",
            "Rounding the back",
            "Not keeping supporting leg active",
            "Holding breath during stretch"
        ],
        "modifications": "Use strap around foot or keep knee slightly bent",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Intense_Side_Stretch_Pose_or_Parsvottanasana_"): {
        "description": "Parsvottanasana - A standing forward fold with a side stretch element.",
        "alignment_cues": [
            "Stand in wide-legged forward fold",
            "Turn one foot out, other foot slightly in",
            "Square hips toward front foot",
            "Fold forward over front leg"
        ],
        "benefits": [
            "Stretches hamstrings and calves",
            "Improves balance and focus",
            "Calms the nervous system",
            "Strengthens legs"
        ],
        "common_mistakes": [
            "Not squaring hips properly",
            "Rounding spine too much",
            "Not keeping back leg straight",
            "Forcing hands to floor"
        ],
        "modifications": "Use blocks under hands or keep hands on shins",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Legs-Up-the-Wall_Pose_or_Viparita_Karani_"): {
        "description": "Viparita Karani - A restorative inversion that calms the nervous system.",
        "alignment_cues": [
            "Lie with legs up against wall",
            "Scoot sitting bones close to wall",
            "Let arms rest by sides",
            "Close eyes and breathe deeply"
        ],
        "benefits": [
            "Relieves tired legs and feet",
            "Calms anxiety and stress",
            "Improves circulation",
            "Aids in better sleep"
        ],
        "common_mistakes": [
            "Sitting too far from wall",
            "Tensing leg muscles",
            "Not supporting lower back if needed",
            "Staying too long initially"
        ],
        "modifications": "Place bolster under lower back or blanket over body",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Locust_Pose_or_Salabhasana_"): {
        "description": "Salabhasana - A backbend that strengthens the entire back body.",
        "alignment_cues": [
            "Lie on belly with arms alongside body",
            "Lift chest, arms, and legs simultaneously",
            "Keep legs straight and together",
            "Reach arms back actively"
        ],
        "benefits": [
            "Strengthens back muscles",
            "Improves posture",
            "Stimulates digestive organs",
            "Builds mental determination"
        ],
        "common_mistakes": [
            "Lifting too high too quickly",
            "Not engaging leg muscles",
            "Hunching shoulders",
            "Holding breath"
        ],
        "modifications": "Lift only chest, or only legs, or place cushion under hips",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Lord_of_the_Dance_Pose_or_Natarajasana_"): {
        "description": "Natarajasana - A standing backbend that embodies grace and strength.",
        "alignment_cues": [
            "Stand on one leg and bend other knee",
            "Grab ankle from inside with same-side hand",
            "Kick foot into hand and lift chest",
            "Reach other arm forward for balance"
        ],
        "benefits": [
            "Improves balance and concentration",
            "Opens chest and hip flexors",
            "Strengthens standing leg",
            "Builds grace and poise"
        ],
        "common_mistakes": [
            "Leaning too far forward",
            "Not kicking foot into hand",
            "Collapsing through chest",
            "Forcing the backbend"
        ],
        "modifications": "Use wall for support or strap around lifted foot",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Low_Lunge_pose_or_Anjaneyasana_"): {
        "description": "Anjaneyasana - A hip-opening lunge that builds strength and flexibility.",
        "alignment_cues": [
            "Step one foot forward into lunge",
            "Lower back knee to floor",
            "Keep front knee over ankle",
            "Lift chest and reach arms up"
        ],
        "benefits": [
            "Opens hip flexors deeply",
            "Strengthens legs and core",
            "Improves balance",
            "Energizes the body"
        ],
        "common_mistakes": [
            "Front knee drifting past ankle",
            "Not sinking hips down",
            "Arching back excessively",
            "Not engaging back leg"
        ],
        "modifications": "Keep hands on front thigh or use cushion under back knee",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Noose_Pose_or_Pasasana_"): {
        "description": "Tadasana - The foundation of all standing poses, teaching perfect posture.",
        "alignment_cues": [
            "Stand with feet hip-width apart",
            "Ground through all four corners of feet",
            "Engage leg muscles and lift kneecaps",
            "Lengthen spine and relax shoulders"
        ],
        "benefits": [
            "Improves posture and alignment",
            "Builds body awareness",
            "Strengthens legs and core",
            "Centers the mind"
        ],
        "common_mistakes": [
            "Locking knees",
            "Shifting weight to one foot",
            "Tensing shoulders",
            "Not engaging core"
        ],
        "modifications": "Stand against wall for alignment reference",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Noose Pose"): {
        "description": "Pasasana - A challenging combination of squat, twist, and bind.",
        "alignment_cues": [
            "Start in deep squat position",
            "Twist torso to one side",
            "Wrap arms around legs to bind",
            "Keep feet parallel and close together"
        ],
        "benefits": [
            "Deeply twists the spine",
            "Opens hips and ankles",
            "Improves balance",
            "Aids digestion"
        ],
        "common_mistakes": [
            "Not maintaining squat depth",
            "Forcing the twist",
            "Lifting heels unnecessarily",
            "Binding too aggressively"
        ],
        "modifications": "Sit on block or practice twist without bind",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Peacock_Pose_or_Mayurasana_"): {
        "description": "Mayurasana - An advanced arm balance that requires significant strength.",
        "alignment_cues": [
            "Kneel and place hands on floor",
            "Point fingers toward feet",
            "Rest elbows against belly",
            "Lean forward and lift legs"
        ],
        "benefits": [
            "Strengthens arms and wrists dramatically",
            "Tones abdominal organs",
            "Improves balance and focus",
            "Builds mental confidence"
        ],
        "common_mistakes": [
            "Not warming up wrists adequately",
            "Attempting without sufficient strength",
            "Placing elbows incorrectly",
            "Not engaging core"
        ],
        "modifications": "Practice the arm position without lifting legs",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Pigeon_Pose_or_Kapotasana_"): {
        "description": "Eka Pada Rajakapotasana - A deep hip opener with many variations.",
        "alignment_cues": [
            "From downward dog, bring one knee forward",
            "Place knee behind wrist, foot toward opposite hip",
            "Extend back leg straight behind you",
            "Square hips and fold forward if comfortable"
        ],
        "benefits": [
            "Opens hips and hip flexors deeply",
            "Releases emotional tension",
            "Improves posture",
            "Prepares for backbends"
        ],
        "common_mistakes": [
            "Sitting on back foot",
            "Not supporting with props if needed",
            "Forcing hip down",
            "Collapsing over front leg"
        ],
        "modifications": "Place cushion under front hip or practice figure-4 stretch",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Plank_Pose_or_Kumbhakasana_"): {
        "description": "Phalakasana - A fundamental strength-building pose.",
        "alignment_cues": [
            "Start in downward dog",
            "Shift forward so shoulders are over wrists",
            "Create straight line from head to heels",
            "Engage core and breathe steadily"
        ],
        "benefits": [
            "Strengthens arms, core, and legs",
            "Improves posture",
            "Builds mental endurance",
            "Prepares for arm balances"
        ],
        "common_mistakes": [
            "Sagging hips",
            "Lifting hips too high",
            "Not engaging leg muscles",
            "Holding breath"
        ],
        "modifications": "Lower knees to floor or place hands on higher surface",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Plow_Pose_or_Halasana_"): {
        "description": "Halasana - An inversion that calms the mind and stretches the spine.",
        "alignment_cues": [
            "Lie on back and lift legs over head",
            "Touch toes to floor behind head",
            "Keep legs straight and together",
            "Support back with hands if needed"
        ],
        "benefits": [
            "Calms the nervous system",
            "Stretches spine and shoulders",
            "Stimulates thyroid gland",
            "Improves circulation"
        ],
        "common_mistakes": [
            "Turning head while in pose",
            "Forcing feet to floor",
            "Not supporting back adequately",
            "Staying too long initially"
        ],
        "modifications": "Keep legs bent or rest feet on chair behind head",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Pose_Dedicated_to_the_Sage_Koundinya_or_Eka_Pada_Koundinyanasana_I_and_II"): {
        "description": "Eka Pada Koundinyasana - An advanced arm balance with a twist.",
        "alignment_cues": [
            "Start in side plank with top leg forward",
            "Hook top leg over same-side arm",
            "Shift weight to hands and lift bottom leg",
            "Keep arms strong and chest open"
        ],
        "benefits": [
            "Strengthens arms and core significantly",
            "Improves balance and coordination",
            "Builds mental focus",
            "Combines strength with flexibility"
        ],
        "common_mistakes": [
            "Not hooking leg properly",
            "Insufficient core strength",
            "Collapsing through chest",
            "Attempting without proper preparation"
        ],
        "modifications": "Practice the arm position and leg hook separately first",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Rajakapotasana"): {
        "description": "King Pigeon Pose - An advanced backbend combining hip opening with heart opening.",
        "alignment_cues": [
            "Start in pigeon pose",
            "Bend back leg and grab foot with hand",
            "Reach other arm back to grab foot",
            "Open chest and breathe deeply"
        ],
        "benefits": [
            "Opens entire front body deeply",
            "Combines hip and heart opening",
            "Builds mental courage",
            "Improves posture dramatically"
        ],
        "common_mistakes": [
            "Not preparing hips adequately",
            "Forcing the backbend",
            "Not warming up shoulders",
            "Attempting too soon in practice"
        ],
        "modifications": "Use strap around back foot or stay in regular pigeon",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Reclining_Hand-to-Big-Toe_Pose_or_Supta_Padangusthasana_"): {
        "description": "Supta Padangusthasana - A supine hamstring stretch with variations.",
        "alignment_cues": [
            "Lie on back with one leg straight up",
            "Hold big toe or use strap around foot",
            "Keep other leg straight on floor",
            "Draw lifted leg closer to torso"
        ],
        "benefits": [
            "Stretches hamstrings and calves",
            "Relieves lower back tension",
            "Improves hip flexibility",
            "Calms the nervous system"
        ],
        "common_mistakes": [
            "Lifting head off floor",
            "Bending bottom leg",
            "Forcing leg closer than comfortable",
            "Not keeping hips square"
        ],
        "modifications": "Use strap around foot or bend bottom knee",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Revolved_Head-to-Knee_Pose_or_Parivrtta_Janu_Sirsasana_"): {
        "description": "Parivrtta Janu Sirsasana - A seated side bend with a twist element.",
        "alignment_cues": [
            "Sit with one leg straight, other knee bent out",
            "Side bend over straight leg",
            "Reach top arm over head toward foot",
            "Twist ribcage toward ceiling"
        ],
        "benefits": [
            "Stretches side body and spine",
            "Opens intercostal muscles",
            "Aids digestion",
            "Calms the mind"
        ],
        "common_mistakes": [
            "Collapsing forward instead of side bending",
            "Not keeping bottom ribs long",
            "Forcing the twist",
            "Holding breath"
        ],
        "modifications": "Place hand on floor for support or use strap",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Scale_Pose_or_Tolasana_"): {
        "description": "Tolasana - An arm balance that lifts the body using core and arm strength.",
        "alignment_cues": [
            "Sit in lotus or cross-legged position",
            "Place hands on floor beside hips",
            "Press down and lift entire body",
            "Keep core engaged and breathe"
        ],
        "benefits": [
            "Strengthens arms and core",
            "Improves balance",
            "Builds mental focus",
            "Develops functional strength"
        ],
        "common_mistakes": [
            "Not pressing hands down firmly",
            "Insufficient core engagement",
            "Attempting without adequate strength",
            "Holding breath"
        ],
        "modifications": "Place hands on blocks for height or practice lifting motion",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Scorpion_pose_or_vrischikasana"): {
        "description": "Vrschikasana - An advanced inversion that combines forearm stand with backbend.",
        "alignment_cues": [
            "Start in forearm stand",
            "Begin to bend knees and arch back",
            "Bring feet toward head",
            "Find balance between inversion and backbend"
        ],
        "benefits": [
            "Strengthens arms and shoulders",
            "Opens entire front body",
            "Improves balance and coordination",
            "Builds mental courage"
        ],
        "common_mistakes": [
            "Not mastering forearm stand first",
            "Forcing the backbend",
            "Collapsing through shoulders",
            "Attempting without proper preparation"
        ],
        "modifications": "Practice against wall or focus on forearm stand first",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Seated_Forward_Bend_pose_or_Paschimottanasana_"): {
        "description": "Paschimottanasana - A fundamental seated forward fold.",
        "alignment_cues": [
            "Sit with legs straight and together",
            "Reach arms up to lengthen spine",
            "Fold forward from hips, not waist",
            "Keep spine long as you fold"
        ],
        "benefits": [
            "Stretches hamstrings and spine",
            "Calms the mind",
            "Stimulates digestive organs",
            "Relieves stress and anxiety"
        ],
        "common_mistakes": [
            "Rounding spine immediately",
            "Forcing forehead to legs",
            "Not engaging leg muscles",
            "Holding breath"
        ],
        "modifications": "Sit on cushion, bend knees, or use strap around feet",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Shoulder-Pressing_Pose_or_Bhujapidasana_"): {
        "description": "Bhujapidasana - An arm balance that requires hip flexibility and arm strength.",
        "alignment_cues": [
            "Start in wide-legged squat",
            "Place hands on floor and thread arms behind thighs",
            "Shift weight to hands and lift feet",
            "Cross ankles if possible"
        ],
        "benefits": [
            "Strengthens arms and core",
            "Improves balance",
            "Opens hips",
            "Builds mental determination"
        ],
        "common_mistakes": [
            "Not getting arms far enough under legs",
            "Insufficient warm-up",
            "Collapsing through chest",
            "Not engaging core"
        ],
        "modifications": "Keep feet on floor or use block under forehead",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Side_Crane_(Crow)_Pose_or_Parsva_Bakasana_"): {
        "description": "Parsva Bakasana - A twisted variation of crane pose.",
        "alignment_cues": [
            "Start in deep squat and twist to one side",
            "Place hands on floor to one side",
            "Hook legs over one arm",
            "Shift weight forward and lift feet"
        ],
        "benefits": [
            "Strengthens arms and core",
            "Deeply twists the spine",
            "Improves balance and focus",
            "Builds confidence"
        ],
        "common_mistakes": [
            "Not twisting deeply enough",
            "Insufficient core strength",
            "Not hooking legs properly",
            "Attempting without mastering regular crane"
        ],
        "modifications": "Practice the twist and arm position separately first",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Side_Plank_Pose_or_Vasisthasana_"): {
        "description": "Vasisthasana - A lateral strength pose that challenges stability.",
        "alignment_cues": [
            "From plank pose, shift to one hand",
            "Stack feet and lift hips",
            "Create straight line from head to feet",
            "Reach top arm toward ceiling"
        ],
        "benefits": [
            "Strengthens arms, core, and legs",
            "Improves balance",
            "Builds lateral stability",
            "Enhances focus"
        ],
        "common_mistakes": [
            "Collapsing through waist",
            "Not stacking shoulders",
            "Putting weight on top hand",
            "Not engaging legs"
        ],
        "modifications": "Lower bottom knee to floor or practice against wall",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Side-Reclining_Leg_Lift_pose_or_Anantasana_"): {
        "description": "Anantasana - A reclining pose that combines balance with hamstring stretch.",
        "alignment_cues": [
            "Lie on side with head propped on hand",
            "Grab big toe of top leg",
            "Extend leg up while keeping torso stable",
            "Keep bottom leg straight and strong"
        ],
        "benefits": [
            "Stretches hamstrings and side body",
            "Improves balance and coordination",
            "Strengthens core",
            "Enhances focus"
        ],
        "common_mistakes": [
            "Rolling backward or forward",
            "Forcing leg higher than comfortable",
            "Not keeping bottom leg active",
            "Tensing shoulders"
        ],
        "modifications": "Use strap around foot or keep knee bent",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Sitting pose 1 (normal)"): {
        "description": "Sukhasana - A simple cross-legged seated position for meditation.",
        "alignment_cues": [
            "Sit cross-legged with shins parallel",
            "Place hands on knees or in lap",
            "Lengthen spine and relax shoulders",
            "Close eyes and breathe naturally"
        ],
        "benefits": [
            "Calms the mind",
            "Improves posture",
            "Opens hips gently",
            "Prepares for meditation"
        ],
        "common_mistakes": [
            "Slouching through spine",
            "Forcing hips to open",
            "Tensing shoulders",
            "Not supporting with props if needed"
        ],
        "modifications": "Sit on cushion or blanket, or use wall support",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Split Pose"): {
        "description": "Hanumanasana - A deep split that requires significant hip flexibility.",
        "alignment_cues": [
            "From low lunge, slowly straighten both legs",
            "Keep hips square and front leg straight",
            "Lower down only as far as comfortable",
            "Use hands for support"
        ],
        "benefits": [
            "Stretches hamstrings and hip flexors deeply",
            "Improves flexibility dramatically",
            "Builds mental patience",
            "Releases emotional tension"
        ],
        "common_mistakes": [
            "Forcing the split",
            "Not keeping hips square",
            "Insufficient warm-up",
            "Ignoring pain signals"
        ],
        "modifications": "Use blocks or bolster under front thigh for support",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Staff_Pose_or_Dandasana_"): {
        "description": "Dandasana - The foundation of all seated poses.",
        "alignment_cues": [
            "Sit with legs straight and together",
            "Place hands beside hips on floor",
            "Lengthen spine and engage leg muscles",
            "Keep shoulders relaxed"
        ],
        "benefits": [
            "Strengthens back and core",
            "Improves posture",
            "Prepares for seated poses",
            "Builds awareness"
        ],
        "common_mistakes": [
            "Slouching through spine",
            "Not engaging leg muscles",
            "Tensing shoulders",
            "Leaning back on hands"
        ],
        "modifications": "Sit on cushion or place hands on blocks",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Standing_big_toe_hold_pose_or_Utthita_Padangusthasana"): {
        "description": "Utthita Hasta Padangusthasana - A standing balance with hamstring stretch.",
        "alignment_cues": [
            "Stand on one leg and lift other leg",
            "Hold big toe with same-side hand",
            "Straighten lifted leg while keeping torso upright",
            "Keep standing leg strong"
        ],
        "benefits": [
            "Improves balance and focus",
            "Stretches hamstrings",
            "Strengthens standing leg",
            "Builds mental concentration"
        ],
        "common_mistakes": [
            "Leaning forward excessively",
            "Not keeping standing leg engaged",
            "Forcing leg higher than comfortable",
            "Losing balance and giving up quickly"
        ],
        "modifications": "Use strap around foot or keep hand on knee",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Standing_Forward_Bend_pose_or_Uttanasana_"): {
        "description": "Uttanasana - A fundamental standing forward fold.",
        "alignment_cues": [
            "Stand with feet hip-width apart",
            "Fold forward from hips, not waist",
            "Let arms hang or hold opposite elbows",
            "Bend knees if hamstrings are tight"
        ],
        "benefits": [
            "Stretches hamstrings and calves",
            "Calms the mind",
            "Relieves stress",
            "Improves circulation"
        ],
        "common_mistakes": [
            "Rounding spine excessively",
            "Locking knees",
            "Not engaging leg muscles",
            "Forcing hands to floor"
        ],
        "modifications": "Bend knees, rest hands on shins, or use blocks",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Standing_Split_pose_or_Urdhva_Prasarita_Eka_Padasana_"): {
        "description": "Urdhva Prasarita Eka Padasana - A standing balance that combines forward fold with leg lift.",
        "alignment_cues": [
            "From standing forward fold, lift one leg high",
            "Keep hips square to floor",
            "Rest hands on floor or blocks",
            "Keep standing leg straight and strong"
        ],
        "benefits": [
            "Stretches hamstrings deeply",
            "Improves balance",
            "Strengthens standing leg",
            "Builds focus and determination"
        ],
        "common_mistakes": [
            "Opening hips instead of keeping them square",
            "Not keeping standing leg engaged",
            "Forcing lifted leg higher",
            "Putting too much weight on hands"
        ],
        "modifications": "Use blocks under hands or keep lifted leg lower",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Supported_Headstand_pose_or_Salamba_Sirsasana_"): {
        "description": "Salamba Sirsasana - The king of poses, an inversion that requires strength and balance.",
        "alignment_cues": [
            "Place forearms on floor with elbows shoulder-width apart",
            "Interlace fingers and place crown of head in hands",
            "Tuck toes and walk feet closer to elbows",
            "Lift legs up slowly and find balance"
        ],
        "benefits": [
            "Improves circulation dramatically",
            "Calms the nervous system",
            "Strengthens shoulders and core",
            "Builds mental confidence"
        ],
        "common_mistakes": [
            "Putting too much weight on head",
            "Widening elbows",
            "Kicking up too aggressively",
            "Not building strength gradually"
        ],
        "modifications": "Practice against wall or with teacher assistance",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Supported_Shoulderstand_pose_or_Salamba_Sarvangasana_"): {
        "description": "Salamba Sarvangasana - The queen of poses, a gentle inversion.",
        "alignment_cues": [
            "Lie on back and lift legs over head",
            "Support back with hands",
            "Straighten legs toward ceiling",
            "Keep most weight on shoulders, not neck"
        ],
        "benefits": [
            "Calms the nervous system",
            "Improves circulation",
            "Stimulates thyroid gland",
            "Relieves stress and fatigue"
        ],
        "common_mistakes": [
            "Too much weight on neck",
            "Not supporting back adequately",
            "Turning head while in pose",
            "Staying too long initially"
        ],
        "modifications": "Use blanket under shoulders or practice legs up wall",
        "difficulty": "Intermediate"
    },
    
    normalize_pose_name("Supta_Baddha_Konasana_"): {
        "description": "Reclining Bound Angle Pose - A restorative hip opener.",
        "alignment_cues": [
            "Lie on back with soles of feet together",
            "Let knees fall open to sides",
            "Place hands on belly or by sides",
            "Close eyes and breathe deeply"
        ],
        "benefits": [
            "Opens hips and groins gently",
            "Calms the nervous system",
            "Relieves stress and anxiety",
            "Aids in digestion"
        ],
        "common_mistakes": [
            "Forcing knees toward floor",
            "Not supporting knees if needed",
            "Tensing shoulders",
            "Not allowing time to settle"
        ],
        "modifications": "Place cushions or blocks under knees for support",
        "difficulty": "Beginner"
    },
    
    normalize_pose_name("Supta_Virasana_Vajrasana"): {
        "description": "Reclining Hero Pose - A deep quad stretch in a reclining position.",
        "alignment_cues": [
            "Sit in hero pose then slowly recline back",
            "Keep knees together and on floor",
            "Support back with hands, forearms, or bolster",
            "Only go as far back as comfortable"
        ],
        "benefits": [
            "Stretches quadriceps deeply",
            "Opens hip flexors",
            "Aids digestion",
            "Calms the mind"
        ],
        "common_mistakes": [
            "Forcing the recline",
            "Letting knees lift off floor",
            "Not using enough support",
            "Staying too long initially"
        ],
        "modifications": "Use bolster or cushions for back support",
        "difficulty": "Intermediate to Advanced"
    },
    
    normalize_pose_name("Tortoise_Pose"): {
        "description": "Kurmasana - A deep forward fold that resembles a turtle retreating into its shell.",
        "alignment_cues": [
            "Sit with legs wide and knees bent",
            "Thread arms under legs",
            "Fold forward and lower chest toward floor",
            "Keep spine as long as possible"
        ],
        "benefits": [
            "Deeply stretches spine and hips",
            "Calms the nervous system",
            "Encourages introspection",
            "Releases tension"
        ],
        "common_mistakes": [
            "Forcing arms under legs",
            "Rounding spine excessively",
            "Not breathing deeply",
            "Pushing beyond comfortable range"
        ],
        "modifications": "Sit on cushion or don't thread arms fully under legs",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Tree_Pose_or_Vrksasana_"): {
        "description": "Vrksasana - A standing balance that cultivates focus and stability.",
        "alignment_cues": [
            "Stand on one leg and place other foot on inner thigh",
            "Avoid placing foot on side of knee",
            "Bring palms together at heart center",
            "Find a focal point to help with balance"
        ],
        "benefits": [
            "Improves balance and concentration",
            "Strengthens legs and core",
            "Opens hips",
            "Builds mental focus"
        ],
        "common_mistakes": [
            "Placing foot on side of knee",
            "Not engaging standing leg",
            "Looking around constantly",
            "Tensing shoulders"
        ],
        "modifications": "Keep toe on floor or use wall for support",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Triangle Pose"): {
        "description": "Utthita Trikonasana - A fundamental standing pose that creates strong foundation.",
        "alignment_cues": [
            "Stand with feet wide apart",
            "Turn one foot out 90 degrees",
            "Reach toward front foot and place hand down",
            "Extend other arm toward ceiling"
        ],
        "benefits": [
            "Stretches legs and side body",
            "Strengthens legs and core",
            "Improves balance",
            "Opens chest and shoulders"
        ],
        "common_mistakes": [
            "Collapsing over front leg",
            "Not keeping back leg straight",
            "Placing hand on knee",
            "Forcing hand to floor"
        ],
        "modifications": "Use block under hand or keep hand on shin",
        "difficulty": "Beginner to Intermediate"
    },
    
    normalize_pose_name("Upward_Bow_(Wheel)_Pose_or_Urdhva_Dhanurasana_"): {
        "description": "Urdhva Dhanurasana - A full wheel backbend that opens the entire front body.",
        "alignment_cues": [
            "Lie on back with knees bent, feet on floor",
            "Place hands by ears with fingers pointing toward shoulders",
            "Press into hands and feet to lift body",
            "Create even arch throughout spine"
        ],
        "benefits": [
            "Opens entire front body",
            "Strengthens arms, legs, and back",
            "Energizes the body",
            "Builds mental courage"
        ],
        "common_mistakes": [
            "Not warming up adequately",
            "Putting too much weight on wrists",
            "Collapsing into lower back",
            "Not engaging leg muscles"
        ],
        "modifications": "Practice bridge pose first or use blocks under hands",
        "difficulty": "Advanced"
    },
    
    normalize_pose_name("Upward_Facing_Two-Foot_Staff_Pose_or_Dwi_Pada_Viparita_Dandasana_"): {
    "description": "Dwi Pada Viparita Dandasana - An advanced backbend performed from headstand or shoulderstand position.",
    "alignment_cues": [
      "From headstand, slowly lower feet to floor behind head",
      "Keep legs straight and press feet down",
      "Maintain lift through chest and shoulders",
      "Keep weight evenly distributed"
    ],
    "benefits": [
      "Opens entire front body deeply",
      "Strengthens back and shoulders",
      "Improves spinal flexibility",
      "Builds mental courage and focus"
    ],
    "common_mistakes": [
      "Collapsing through shoulders",
      "Not keeping legs straight",
      "Rushing the transition",
      "Inadequate warm-up"
    ],
    "modifications": "Practice bridge pose variations first or use wall support",
    "difficulty": "Advanced"
  },
    
  normalize_pose_name("Upward_Plank_Pose_or_Purvottanasana_"): {
    "description": "Purvottanasana - A backbend that strengthens the entire back body.",
    "alignment_cues": [
      "Sit in staff pose with hands behind hips",
      "Press into hands and feet to lift hips",
      "Create straight line from head to heels",
      "Keep chest open and shoulders over wrists"
    ],
    "benefits": [
      "Strengthens arms, shoulders, and back",
      "Opens chest and hip flexors",
      "Improves posture",
      "Builds functional strength"
    ],
    "common_mistakes": [
      "Dropping hips",
      "Collapsing through shoulders",
      "Not engaging leg muscles",
      "Placing hands too close to body"
    ],
    "modifications": "Keep knees bent or practice on forearms",
    "difficulty": "Intermediate"
  },
  
  normalize_pose_name("Reverse Warrior Pose"): {
    "description": "Viparita Virabhadrasana - A side bend that opens the side body while maintaining warrior stance.",
    "alignment_cues": [
      "From Warrior II, place back hand on back leg",
      "Reach front arm over head in side bend",
      "Keep front thigh parallel to floor",
      "Maintain strength in both legs"
    ],
    "benefits": [
      "Opens side body and chest",
      "Strengthens legs and core",
      "Improves balance",
      "Energizes the body"
    ],
    "common_mistakes": [
      "Putting too much weight on back hand",
      "Losing warrior stance in legs",
      "Collapsing forward",
      "Not breathing deeply"
    ],
    "modifications": "Keep front hand on hip or use shorter stance",
    "difficulty": "Beginner to Intermediate"
  },
  
  normalize_pose_name("Virasana_or_Vajrasana"): {
    "description": "Hero Pose - A kneeling pose that stretches the quadriceps and prepares for meditation.",
    "alignment_cues": [
      "Kneel with tops of feet flat on floor",
      "Sit back between heels",
      "Keep knees together",
      "Lengthen spine and relax shoulders"
    ],
    "benefits": [
      "Stretches quadriceps and ankles",
      "Improves posture",
      "Aids digestion",
      "Calms the mind"
    ],
    "common_mistakes": [
      "Forcing the sit if knees are tight",
      "Letting knees splay apart",
      "Slouching through spine",
      "Not using props when needed"
    ],
    "modifications": "Sit on cushion or block between heels",
    "difficulty": "Beginner to Intermediate"
  },
  
  normalize_pose_name("Warrior_I_Pose_or_Virabhadrasana_I_"): {
    "description": "Virabhadrasana I - A standing lunge pose that builds strength and focus.",
    "alignment_cues": [
      "Step one foot back into lunge position",
      "Keep back foot at 45-degree angle",
      "Square hips toward front",
      "Reach arms overhead"
    ],
    "benefits": [
      "Strengthens legs and core",
      "Opens hip flexors and chest",
      "Improves balance and focus",
      "Builds mental determination"
    ],
    "common_mistakes": [
      "Not keeping back foot grounded",
      "Allowing back hip to open",
      "Arching back excessively",
      "Narrow stance"
    ],
    "modifications": "Use blocks under hands or shorten stance",
    "difficulty": "Beginner to Intermediate"
  },
  
  normalize_pose_name("Warrior_II_Pose_or_Virabhadrasana_II_"): {
    "description": "Virabhadrasana II - A fundamental standing pose that builds strength and endurance.",
    "alignment_cues": [
      "Stand with feet wide, turn one foot out 90 degrees",
      "Bend front knee over ankle",
      "Keep back leg straight and strong",
      "Extend arms parallel to floor"
    ],
    "benefits": [
      "Strengthens legs and core",
      "Opens hips and chest",
      "Improves concentration",
      "Builds stamina"
    ],
    "common_mistakes": [
      "Letting front knee cave inward",
      "Leaning torso over front leg",
      "Not grounding back foot",
      "Dropping arms"
    ],
    "modifications": "Use wall behind back leg for support or shorten stance",
    "difficulty": "Beginner"
  },
  
  normalize_pose_name("Warrior_III_Pose_or_Virabhadrasana_III_"): {
    "description": "Virabhadrasana III - A challenging balance pose that requires strength and focus.",
    "alignment_cues": [
      "From Warrior I, shift weight to front foot",
      "Hinge forward and lift back leg",
      "Extend arms forward or out to sides",
      "Create straight line from head to lifted heel"
    ],
    "benefits": [
      "Improves balance and coordination",
      "Strengthens legs and core",
      "Builds mental focus",
      "Enhances proprioception"
    ],
    "common_mistakes": [
      "Opening lifted hip",
      "Dropping chest too low",
      "Not engaging standing leg",
      "Looking around instead of finding focal point"
    ],
    "modifications": "Use wall or chair for support, or keep hands on hips",
    "difficulty": "Intermediate to Advanced"
  }
}

def extract_keypoints(image_path):
    img = cv2.imread(image_path)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose_detector.process(rgb)
    if results.pose_landmarks:
        keypoints = []
        for lm in results.pose_landmarks.landmark:
            keypoints.extend([lm.x, lm.y, lm.z, lm.visibility])
        return np.array(keypoints)
    return None

@app.route("/", methods=["GET"])
def index():
    return "\u2705 Yoga Pose Detection API is running. Use POST /predict to upload an image."

@app.route("/predict", methods=["POST"])
def predict_pose():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    img_path = "temp.jpg"
    image.save(img_path)

    keypoints = extract_keypoints(img_path)
    os.remove(img_path)

    if keypoints is None:
        return jsonify({'error': 'No pose landmarks detected'}), 400

    keypoints = keypoints / np.linalg.norm(keypoints)
    keypoints = keypoints.reshape(1, -1)

    prediction = model.predict(keypoints, verbose=0)
    predicted_idx = int(np.argmax(prediction))
    confidence = float(prediction[0][predicted_idx])
    predicted_pose = class_names[predicted_idx]

    feedback_data = pose_feedback.get(predicted_pose, {})

    return jsonify({
        'predicted_pose': predicted_pose,
        'confidence': round(confidence * 100, 2),
        'feedback': feedback_data
    })

if __name__ == "__main__":
    app.run(debug=True)
