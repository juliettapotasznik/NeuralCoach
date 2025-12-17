DROP TABLE IF EXISTS exercise_body_parts CASCADE;
DROP TABLE IF EXISTS exercises CASCADE;
DROP TABLE IF EXISTS body_parts CASCADE;
CREATE TABLE body_parts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    media_file TEXT NOT NULL,
    attribution TEXT NOT NULL,
    description TEXT NOT NULL,
    is_analyzable BOOLEAN DEFAULT FALSE
);

CREATE TABLE exercise_body_parts (
    exercise_id INTEGER NOT NULL,
    body_part_id INTEGER NOT NULL,
    PRIMARY KEY (exercise_id, body_part_id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
    FOREIGN KEY (body_part_id) REFERENCES body_parts(id) ON DELETE CASCADE
);

CREATE INDEX idx_exercise_id ON exercise_body_parts(exercise_id);
CREATE INDEX idx_body_part_id ON exercise_body_parts(body_part_id);

INSERT INTO body_parts (name) VALUES 
    ('Back'), 
    ('Legs'), 
    ('Chest'), 
    ('Arms'), 
    ('Shoulders'), 
    ('ABS');

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Assisted Parallel Grip Pull Up',
    'AssistedParallelGripPullUp.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Assisted Parallel Grip Pull Up Exercise for Back</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set the weight: Select the amount of weight to "assist" you on the machine. (More weight = easier, as it counter-balances your body). Position yourself: Step onto the foot bar or knee pad. Grip the parallel (neutral grip, palms facing each other) handles. Starting position: Let the pad lift you up. Start from a full hang with your arms extended and your shoulders "unpacked" (up by your ears). Engage lats: Pull your shoulder blades down and back (scapular retraction) to engage your back. Pull up: Exhale and pull your body up, driving your elbows down towards your hips. Squeeze at the top: Continue pulling until your chin is above your hands. Squeeze your back muscles at the top. Lower with control: Inhale and slowly lower yourself back down to the starting (full hang) position. Repeat. Coach Tips: Avoid letting your shoulders shrug up by your ears during the pull. Keep them down and back. Control the entire movement. Don''t "drop" on the way down, and don''t use momentum to "kip" on the way up. Focus on pulling with your back and lats, not just your arms.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Back Squat',
    'BarbellBackSquat.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Back Squat Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set the bar: Set the barbell in a squat rack at the height of your mid-chest or upper shoulders. Position the bar: Step under the bar and place it across your upper back (on your traps), not on your neck. Grip the bar firmly. Unrack: Stand up to unrack the weight. Take 2-3 steps back and set your feet shoulder-width apart, with toes pointed slightly out. Brace: Take a deep breath, brace your core, and keep your chest up. Squat down: Initiate the movement by pushing your hips back and bending your knees. Lower your hips down and back, as if sitting in a chair. Hit depth: Continue lowering until your hips are at least parallel to the floor (or as low as your mobility allows), keeping your back straight. Drive up: Exhale and drive through your heels and mid-foot to stand back up, squeezing your glutes at the top. Repeat. Coach Tips: Keep your chest up and your back in a straight, neutral position. Do not let your upper back round or your chest collapse. Your knees should track in line with your toes. Do not let them "cave in" (valgus collapse). Drive through your heels, not the balls of your feet.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Bench Press',
    'BarbellBenchPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Bench Press Exercise for Chest</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Lie on the bench: Lie flat on the bench with your eyes directly under the bar. Plant your feet firmly on the floor. Grip the bar: Grasp the barbell with an overhand grip, slightly wider than shoulder-width. Squeeze your shoulder blades together and "screw" them into the bench. Unrack the bar: Lift the bar from the rack and stabilize it directly over your mid-chest with your arms straight. Lower the bar: Slowly and with control, lower the bar to your lower or mid-chest. Your elbows should be tucked slightly (not flared out at 90 degrees). Press: Explosively push the bar back up to the starting position, extending your elbows and squeezing your chest. Maintain contact: Keep your glutes and shoulder blades in contact with the bench throughout the press. Repeat: Repeat the exercise for the desired number of repetitions, then safely re-rack the weight. Coach Tips: Keep your feet firmly planted on the ground throughout the exercise to maintain stability. Focus on retracting your shoulder blades (scapular retraction) – this creates a stable platform to press from and protects your shoulders. Control the eccentric (lowering) phase – do not let the bar bounce off your chest.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Bench Squat',
    'BarbellBenchSquat.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Bench Squat Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Set up: Place a barbell in a squat rack. Place a sturdy box or bench behind you. The height should be set so your thighs are at parallel (or just below) when you sit. Position the bar: Place the barbell on your upper back/traps. Unrack the weight. Set your stance: Take a few steps back until you are standing directly in front of the box. Your stance can be slightly wider than a normal squat. Hinge and sit: Inhale, brace your core, and push your hips back first. Sit back onto the box in a controlled manner. Pause: Sit on the box completely, allowing your shin muscles to relax for a second. Keep your back tight and chest up. Do not bounce. Drive up: Explode up off the box by driving your heels into the floor and squeezing your glutes. Exhale on the way up. Repeat: Repeat the movement, sitting back onto the box for each rep. Coach Tips: The key is to sit back onto the box, not just squat down. This emphasizes the posterior chain (glutes, hamstrings). Keep your core and upper back tight the entire time, especially when you are seated. Do not "relax" and round your back. Drive up explosively from the "dead stop" on the box.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Bent Over Row',
    'BarbellBentOverRow.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Bent Over Row Exercise for Back</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Grip the bar: Stand with your feet shoulder-width apart and grip the barbell with an overhand (or underhand) grip, slightly wider than your shoulders. Set your position: Bend your knees slightly and hinge forward at the hips until your torso is nearly parallel to the floor. Keep your back straight and engaged (neutral spine). Starting movement: The bar should hang with your arms fully extended, directly below your shoulders. Pull: Pull the barbell towards your lower chest or upper abdomen. Lead with your elbows, keeping them close to your body and pulling them back. Squeeze your back: At the top of the movement, squeeze your shoulder blades together and contract your back muscles. Return to start: Slowly and with control, lower the barbell back to the starting position, maintaining a straight back. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Maintaining a flat, neutral back is the absolute priority. Do not round your lower back. Avoid using momentum or "jerking" the weight up. The movement should be controlled. Focus on initiating the pull with your shoulder blades, not just your arms.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Bulgarian Split Squat',
    'BarbellBulgarianSplitSquat.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Bulgarian Split Squat Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set up: Place a bench behind you. Set a barbell in a squat rack and load it on your upper back/traps, just like a regular squat. Position your feet: Unrack the bar. Step forward and place one foot (e.g., your left) on the bench behind you, with your shoelaces down or toes planted. Find your stance: Hop your front (right) foot forward until you find a stable lunge stance. Your chest should be up and core braced. Squat down: Inhale and lower your body straight down, bending your front knee. Your back knee will move towards the floor. Hit depth: Lower until your front thigh is at least parallel to the floor. Drive up: Exhale and drive through your front heel to push yourself back up to the starting position. Repeat: Complete all repetitions on one leg before carefully switching to the other. Coach Tips: This is an advanced exercise; start with light weight to master the balance. Keep your front knee tracking in line with your front foot. Do not let it collapse inward. Your front foot should be far enough forward that your heel stays planted on the ground.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Glute Bridge',
    'BarbellGluteBridge.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Glute Bridge Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Lie on the floor: Lie flat on your back on the floor, with your knees bent and feet flat on the ground, hip-width apart. Position the bar: Roll a loaded barbell over your legs so it rests in your hip crease (use a pad for comfort). Grip the bar: Hold the barbell with both hands to keep it stable. Thrust: Exhale and drive through your heels to lift your hips off the floor until your body forms a straight line from your shoulders to your knees. Squeeze at the top: Pause at the top and squeeze your glutes as hard as you can. Lower with control: Inhale and slowly lower your hips back down to the floor. Repeat: Repeat the movement, ensuring your heels stay planted. Coach Tips: Keep your chin slightly tucked. This helps engage your glutes more and prevents you from arching your back. At the top, your shins should be roughly vertical. This exercise has a shorter range of motion than a hip thrust and targets the glutes intensely.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Hip Thrust',
    'BarbellHipThrust.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Hip Thrust Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Set up: Sit on the floor with your upper back (just below the shoulder blades) resting against the side of a flat bench. Position the bar: Roll a loaded barbell over your legs so it rests in your hip crease (a bar pad is highly recommended). Position your feet: Plant your feet flat on the floor, shoulder-width apart, with knees bent. Thrust: Grasp the bar. Exhale and drive through your heels to lift your hips up until your torso and thighs are parallel to the floor. Squeeze at the top: Pause at the top and squeeze your glutes hard. Your shins should be vertical, and your gaze should be forward (chin tucked). Lower with control: Inhale and lower your hips back down towards the floor, maintaining control. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Keep your chin tucked to your chest. Do not look up at the ceiling. Your shins must be vertical at the top of the lift. Adjust your feet if they are not. The movement is a hinge from the hips, driven by your glutes, not by arching your lower back.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Incline Bench Press',
    'BarbellInclineBenchPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Incline Bench Press Exercise for Chest</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Set the bench: Adjust the bench to an incline angle, typically between 30 and 45 degrees. Lie on the bench: Lie down on the bench, planting your feet firmly on the floor. Grip the bar with an overhand grip, slightly wider than shoulder-width. Unrack the bar: Lift the bar from the rack and stabilize it over your upper chest with your arms straight. Keep your shoulder blades retracted. Lower the bar: Slowly lower the bar towards your upper chest (around your collarbone). Press: Explosively push the bar back up to the starting position, focusing on contracting the upper part of your chest. Maintain position: Ensure your glutes and shoulder blades remain in contact with the bench. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Just like the flat bench, keep your shoulder blades pulled back and down to protect your shoulders. Keep your wrists straight and stacked over your forearms. Focus on "driving" the weight up with your upper pecs; the bench angle does most of the work, but your focus helps.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Preacher Bicep Curl',
    'BarbellPreacherBicepCurl.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Preacher Bicep Curl Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the bench: Set the seat height so that your armpits fit snugly against the top edge of the preacher bench pad. Grip the bar: Sit down and grab the barbell (an EZ-curl bar is often preferred to reduce wrist strain) with an underhand, shoulder-width grip. Set your position: Rest the backs of your upper arms (triceps) flat on the pad. Your arms should be nearly fully extended at the bottom. Curl: Slowly curl the weight up towards your shoulders. Focus entirely on using your biceps. Squeeze your bicep: At the top of the movement, pause for a second and squeeze your biceps hard. Return to start: Slowly and with control, lower the barbell back to the starting position. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: The key is to keep your triceps glued to the pad throughout the entire set. Avoid using your shoulders or "cheating" the weight up. This is an isolation exercise. Control the lowering phase; do not let the weight just drop. Stop just short of full elbow lockout to maintain tension.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Barbell Standing Shoulders Press',
    'BarbellStandingShouldersPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Barbell Standing Shoulders Press Exercise for Shoulders</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set the bar: Set the barbell in a rack at chest height. Grip the bar with an overhand grip, slightly wider than shoulder-width. Starting position: Unrack the bar and take a step back. Stand tall, feet shoulder-width apart. The bar should rest on your upper chest and front shoulders. Elbows should be pointing slightly forward. Brace your core: Take a deep breath, tighten your core, and squeeze your glutes to stabilize your torso. Press: Explosively press the bar vertically overhead. As the bar passes your forehead, slightly "push" your head through under the bar. Lockout: Finish the movement with your elbows fully locked out, with the bar stable over the middle of your head. Return to start: Slowly and with control, lower the bar back to the starting position on your upper chest. Move your head back slightly to make room. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: This is a full-body lift. Bracing your abs and glutes is critical for stability and preventing back injury. Do not hyperextend your lower back to "cheat" the press. Keep your forearms as vertical as possible in the bottom position for an efficient transfer of force.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Burpee Cardio',
    'BurpeeCardio.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Burpee Cardio Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Start standing: Stand tall with your feet shoulder-width apart and your arms at your sides. Squat and plant: Lower your body into a deep squat and place your hands on the floor directly in front of your feet. Kick back to plank: Explosively kick both feet back at the same time, landing in a high plank (push-up) position. Your body should be in a straight line. Perform a push-up: Lower your chest to the floor in a full push-up. Kick forward: Explosively jump both feet forward, landing them back near your hands in the squat position. Jump: From the squat, immediately jump straight up as high as you can, extending your arms overhead. Repeat: Land softly on the balls of your feet and immediately move into the next repetition. Coach Tips: Keep your core tight throughout the entire movement, especially in the plank and during the push-up, to protect your lower back. Land softly after the jump to minimize impact on your knees and ankles. This is a cardio exercise; find a consistent, challenging rhythm you can maintain.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Burpee No Jump Cardio',
    'BurpeeNoJumpCardio.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Burpee No Jump Cardio Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Start standing: Stand tall with your feet shoulder-width apart. Squat and plant: Lower your body into a squat and place your hands on the floor in front of you. Step back to plank: Step one foot back, and then the other, to arrive in a high plank position. Perform a push-up (optional): You can perform a standard push-up or a modified push-up from your knees. Step forward: Step one foot forward, and then the other, to return to the bottom of the squat position. Stand up: From the squat, stand up tall, driving through your heels and squeezing your glutes at the top. Repeat: Immediately begin the next repetition by squatting back down. Coach Tips: This is a fantastic low-impact alternative. Focus on maintaining good form and a brisk, steady pace. Keep your core engaged to prevent your hips from sagging when you step back into the plank. Even without the jump, be explosive in your "stand up" phase to keep your heart rate high.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Bayesian Curl',
    'CableBayesianCurl.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Bayesian Curl Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a single cable pulley to the lowest (floor) position. Attach a D-handle. Position yourself: Grab the handle with an underhand grip (palm facing up). Stand in position: Step forward, away from the machine, so you are facing the opposite direction. Your working arm will be pulled straight back behind your torso. This is the starting position. Curl: Exhale and, keeping your elbow locked in place behind your body, curl the handle up towards your shoulder. Squeeze your bicep: Pause at the top of the movement and squeeze your bicep hard. Return to start: Inhale and slowly lower the handle, letting your arm extend fully back into the stretched position. Repeat: Complete all repetitions on one arm before switching to the other side. Coach Tips: The key to this exercise is keeping your elbow pulled back behind your torso. Do not let it drift forward. Focus on the deep stretch at the bottom of the movement and the intense contraction at the top. This is an isolation exercise; use a controlled weight and avoid using momentum.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Bench Fly',
    'CableBenchFly.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Bench Fly Exercise for Chest</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the cables: Set both pulleys to their lowest (floor) positions. Attach a D-handle to each. Position the bench: Place a flat bench in the center, equidistant from both pulleys. Position yourself: Lie flat on the bench. Grab both handles (you may need a partner to hand them to you). Starting position: Extend your arms straight up over your chest, palms facing each other. Maintain a slight, constant bend in your elbows. Lower (Fly): Inhale and slowly lower your arms out to your sides in a wide, sweeping arc. Lower until you feel a good stretch in your chest. Squeeze together: Exhale and "hug the tree," reversing the motion to bring the handles back together over your chest. Squeeze your pecs hard at the top. Repeat: Repeat the movement, keeping the slight bend in your elbows. Coach Tips: Do not change your elbow bend during the rep; this is a "fly," not a "press." Keep your shoulders "packed" (down and back) into the bench. Do not let them roll forward. The low cable position provides a unique line of pull and constant tension.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Bench Press',
    'CableBenchPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Bench Press Exercise for Chest</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cables: Set both pulleys to their lowest (floor) positions. Attach a D-handle to each. Position the bench: Place a flat bench in the center, equidistant from both pulleys. Position yourself: Lie flat on the bench. Grab both handles and hold them at your chest, similar to the bottom of a dumbbell press. Press: Exhale and press the handles up and slightly in, so they meet over the center of your chest. Squeeze at the top: Squeeze your chest muscles at the peak of the contraction, with your arms fully extended. Lower with control: Inhale and slowly lower the handles back down to the starting position at the sides of your chest. Repeat: Repeat the exercise, keeping your feet planted and your back on the bench. Coach Tips: Unlike a dumbbell press, the cables allow you to actively pull your hands together at the top for a stronger peak contraction. Control the negative (lowering) phase; don''t let the weights pull you apart. Keep your elbows tucked at about a 45-degree angle, not flared out.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Bicep Curl',
    'CableBicepCurl.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Bicep Curl Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a cable pulley to the lowest (floor) position. Attach a straight bar or an EZ-curl bar. Stand in position: Stand facing the machine, feet shoulder-width apart. Grip the bar: Grasp the bar with an underhand (supinated) grip, hands about shoulder-width apart. Take one step back to create tension. Curl: Exhale and curl the bar up towards your chest. Keep your elbows pinned to your sides. Squeeze your bicep: Pause at the top of the movement and squeeze your biceps hard. Lower with control: Inhale and slowly lower the bar back to the starting position, allowing your arms to fully extend. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Keep your elbows locked in position at your sides. Do not let them swing forward or back. Avoid leaning back or using momentum to "swing" the weight up. Control the negative (lowering) phase to keep constant tension on the biceps.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Close Grip Pulldown',
    'CableCloseGripPulldown.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Close Grip Pulldown Exercise for Back</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a pulley to the highest position. Attach a straight bar or EZ-curl bar. Position yourself: Sit at the lat pulldown station and secure your knees firmly under the pads. Grip the bar: Grasp the bar with a close, underhand (supinated) grip. Your hands should be about 6-8 inches apart. Starting position: Lean back slightly (10-15 degrees), keep your chest up, and extend your arms fully. Pull: Exhale and pull the bar down to your upper chest. Drive your elbows down and back, keeping them close to your body. Squeeze at the bottom: Squeeze your lats and biceps hard at the peak contraction. Return with control: Inhale and slowly let the bar return to the starting position, allowing your lats to stretch fully. Coach Tips: This variation heavily involves the biceps, but the focus should still be on initiating the pull with your back (lats). Keep your chest "proud" and avoid rounding your back or shoulders. Do not use your torso to swing the weight down.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Close Hammer Grip Pulldown',
    'CableCloseHammerGripPulldown.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Close Hammer Grip Pulldown Exercise for Back</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a pulley to the highest position. Attach a "V-bar" (close, neutral/hammer grip handle). Position yourself: Sit at the lat pulldown station and secure your knees firmly under the pads. Grip the handle: Grasp the V-bar with both hands, palms facing each other. Starting position: Lean back slightly, keep your chest up, and extend your arms fully to feel a stretch in your lats. Pull: Exhale and pull the handle down to your upper chest. Focus on driving your elbows down and back. Squeeze at the bottom: Pause and squeeze your lats and mid-back muscles. Return with control: Inhale and slowly let the handle return to the starting position, maintaining control and keeping your chest up. Coach Tips: This neutral grip is often more comfortable for the shoulders and allows for a strong back contraction. Keep your torso stable. Avoid swinging back and forth with the movement. Think about pulling your "shoulder blades into your back pockets."'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable External Shoulder Rotation',
    'CableExternalShoulderRotation.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable External Shoulder Rotation Exercise for Shoulders</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a single cable pulley to be in line with your elbow. Attach a D-handle (or you can just grip the cable''s ball-stopper). Position yourself: Stand sideways to the machine. If your right arm is working, your left shoulder should be closest to the machine. Set your arm: Bend your working (right) elbow to 90 degrees and "pin" it to your side. You can use a small, rolled-up towel between your elbow and your ribs to ensure it stays in place. Grip and start: Grasp the handle. Your forearm should be across your stomach, parallel to the floor. Rotate out: Exhale and, keeping your elbow locked to your side, slowly rotate your forearm outwards (externally) as far as it will comfortably go. Return with control: Inhale and slowly return your forearm to the starting position across your stomach. Repeat: Complete all repetitions on one side before switching. Coach Tips: This is a rotator cuff exercise, not a strength lift. Use very light weight and focus on perfect form. The movement must be a "rotation" from the shoulder joint. Do not let your elbow drift away from your body. Do not twist your torso; all movement should be isolated to the shoulder.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Half Kneeling Face Pull',
    'CableHalfKneelingFacePull.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Half Kneeling Face Pull Exercise for Shoulders</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a cable pulley to head height or slightly above. Attach a rope handle. Position yourself: Get into a half-kneeling (lunge) stance facing the machine. This provides a very stable base. Grip the rope: Grasp the rope handle with both hands, palms facing each other (neutral grip) or palms down (overhand). Extend your arms straight out. Pull: Exhale and pull the rope towards your face. As you pull, "pull the rope apart," driving your elbows high and back. Squeeze at the top: Squeeze your rear deltoids and upper back muscles. Your hands should end up next to your ears or temples. Return with control: Inhale and slowly extend your arms back to the starting position, resisting the pull of the weight. Repeat: Repeat the movement for the desired number of repetitions. Coach Tips: Focus on "pulling the rope apart" as you pull it to your face. This externally rotates the shoulder and engages the rear delts. Keep your chest up and core braced. Do not let your ribs flare or your lower back arch. Initiate the pull with your rear shoulders and upper back, not with your biceps.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Half Kneeling Single Arm Row',
    'CableHalfKneelingSingleArmRow.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Half Kneeling Single Arm Row Exercise for Back</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the cable: Set a single cable pulley to a low position, about mid-shin height. Attach a D-handle. Position yourself: Get into a half-kneeling stance sideways to the machine. If you are rowing with your right arm, your left knee should be down and your right foot forward. Grip and brace: Grab the handle with your right hand using a neutral grip (palm facing in). Brace your core and keep your chest up. Row: Exhale and pull the handle back towards your hip/rib cage. Drive your elbow back and keep it close to your body. Squeeze at the top: Squeeze your lat and mid-back muscles at the peak of the contraction. Avoid twisting your torso. Return with control: Inhale and slowly extend your arm back to the starting position, allowing your shoulder blade to stretch forward. Repeat: Complete all repetitions on one side before switching your stance and arm. Coach Tips: The half-kneeling stance prevents you from using "body English" or momentum. Your torso should remain stable and facing forward. Focus on pulling with your back muscles, not just your arm. Keep your head and spine in a neutral, straight line.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable High Pulley Rope Tricep Extension',
    'CableHighPulleyRopeTricepExtension.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable High Pulley Rope Tricep Extension Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a pulley to the highest position on the cable machine. Attach a rope handle. Grip the rope: Grasp the rope handle with both hands using a neutral (palms-facing) grip. Position yourself: Stand facing the machine, feet shoulder-width apart. Lean forward slightly at the hips. Start with your elbows bent at 90 degrees and "pinned" to your sides. Extend: Exhale and push the rope down towards your thighs by extending your elbows. Separate and squeeze: As you reach the bottom, separate your hands (pulling the rope apart) and squeeze your triceps hard. Return with control: Inhale and slowly let your arms bend back to the 90-degree starting position. Keep your elbows in place. Repeat: Repeat the movement, ensuring only your forearms are moving. Coach Tips: Keep your elbows locked by your sides. Do not let them drift forward or flare out. The "pull apart" at the bottom of the movement maximizes the contraction in the triceps. Avoid using your back or shoulders to "cheat" the weight down. Isolate the triceps.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Kneeling Crunch',
    'CableKneelingCrunch.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Kneeling Crunch Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a pulley to the highest position. Attach a rope handle. Position yourself: Kneel on the floor in front of the machine. You can use a mat for your knees. Grip the rope: Grasp the rope and pull it down so the handles are on either side of your head (by your ears or upper chest). Starting position: Hinge slightly at your hips so there is tension on your abs. Keep your hips stationary. Crunch: Exhale and "curl" your spine, pulling your elbows down towards your knees. Squeeze your abs: Pause at the bottom and squeeze your abdominal muscles hard. Return with control: Inhale and slowly uncurl, resisting the weight as you return to the starting position. Coach Tips: The movement should be a spinal "curl" (like a crunch), not a hip hinge. Your hips should stay relatively still. Do not pull with your arms or neck. Your arms just hold the rope in place; your abs do all the work. Exhale forcefully as you crunch to get a deeper contraction.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Kneeling Donkey Kickback',
    'CableKneelingDonkeyKickback.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Kneeling Donkey Kickback Exercise for Glute</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a single cable pulley to the lowest (floor) position. Attach an ankle strap. Position yourself: Attach the strap to one ankle. Get on all fours (quadruped position) facing away from the machine. Starting position: Your hands should be directly under your shoulders and your knees under your hips. Your working leg (with the strap) should be bent at 90 degrees. Kick back: Exhale and, keeping the 90-degree bend in your knee, drive your heel straight back and up toward the ceiling. Squeeze your glute: Squeeze your glute hard at the top of the movement. Your thigh should be almost parallel to the floor. Return with control: Inhale and slowly bring your knee back down to the starting position, maintaining tension. Repeat: Complete all repetitions on one leg before switching the ankle strap to the other. Coach Tips: Crucial: Do not let your lower back arch or sag. Keep your core tight and your back flat (like a tabletop) throughout the movement. The motion should be driven 100% by your glute, not by arching your back. Keep the 90-degree bend in your knee; don''t just "kick" your foot.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Leaning Lateral Raise',
    'CableLeaningLateralRaise.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Leaning Lateral Raise Exercise for Shoulders</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a single cable pulley to the lowest (floor) position. Attach a D-handle. Position yourself: Stand sideways to the machine. Grab the machine''s frame or upright with your non-working hand for support. Lean: Lean your body away from the machine until your supporting arm is straight. This creates a stable, angled position. Grip and start: Grasp the D-handle with your working (outside) hand. The handle should be in front of your thighs. Raise: Exhale and, keeping your arm straight (with a slight bend in the elbow), raise the handle out to your side. Squeeze at the top: Raise the handle until your arm is parallel to the floor. Pause and squeeze your side deltoid. Lower with control: Inhale and slowly lower the handle back down to the starting position. Repeat for all reps, then switch sides. Coach Tips: The "lean" allows you to keep tension on the deltoid through a greater range of motion, especially at the bottom. Keep your torso stable and braced; do not use momentum or "swing" your body. Lead the movement with your elbow, not your hand, and keep your thumb pointing slightly down.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable One Arm Rope Tricep Pushdown',
    'CableOneArmRopeTricepPushdown.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable One Arm Rope Tricep Pushdown Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the cable: Set a pulley to the highest position. Attach a D-handle, a single rope, or just grab the ball-stopper of the cable. Grip the handle: Grasp the handle with one hand using an overhand or neutral grip. Position yourself: Stand facing the machine. "Pin" your working elbow to your side. Your forearm should be parallel to the floor (90-degree bend). Extend: Exhale and push the handle straight down until your arm is fully extended. Squeeze your tricep: Pause at the bottom and squeeze your tricep hard. Return with control: Inhale and slowly let your arm bend back to the 90-degree starting position. Repeat: Complete all repetitions on one arm before switching to the other. Coach Tips: Your elbow must stay locked in place at your side. Only your forearm should move. If you use a rope, you can twist your palm down (pronate) at the bottom for an even stronger contraction. This is an isolation exercise. Don''t let your shoulder or back get involved in the movement.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Shrug',
    'CableShrug.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Shrug Exercise for Back</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the cable: Set both pulleys to their lowest (floor) positions. Attach a D-handle to each cable. (Alternatively, use a low pulley and a straight bar). Grip the handles: Grasp the handles with your arms straight at your sides. Position yourself: Stand tall in the center, with your chest up and shoulders pulled back and down. Shrug: Exhale and elevate your shoulders straight up toward your ears. Squeeze your traps: Squeeze your trapezius (trap) muscles as hard as you can at the top of the movement. Lower with control: Inhale and slowly lower your shoulders back down to the starting position. Let them get a full stretch at the bottom. Repeat: Repeat the movement, focusing only on the "up and down" motion of the shoulders. Coach Tips: Do not roll your shoulders forward or backward. The movement is purely vertical (up and down). Keep your arms straight throughout the exercise. Do not bend your elbows to "help" lift the weight. Focus on the peak contraction and the deep stretch at the bottom of each rep.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Step Up',
    'CableStepUp.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Step Up Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a single cable pulley to the lowest (floor) position. Attach a D-handle. Position yourself: Place a sturdy box or bench in front of the cable machine. Stand facing the machine. Grip and start: Grab the handle with the opposite hand (e.g., if stepping up with your left leg, hold the cable in your right hand). Place your entire left foot on the box. Step up: Exhale and drive through your front (left) heel to step up onto the box. Bring your right knee up into a high-knee position for balance. Balance: Stand tall at the top. The cable will provide resistance, forcing your core and standing leg to stabilize. Step down with control: Inhale and slowly step back down with your right leg, followed by your left, returning to the floor. Repeat: Complete all repetitions on one leg before switching the handle and your stepping leg. Coach Tips: Focus on pushing through the heel of your top leg. Avoid "pushing off" with your back leg. The cable adds "contralateral" load, which is excellent for core and hip stability. Keep your torso upright. Control the descent (stepping down); don''t just drop back to the floor.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Upright Row',
    'CableUprightRow.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Upright Row Exercise for Shoulders</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the cable: Set a pulley to the lowest (floor) position. Attach a straight bar or EZ-curl bar. Grip the bar: Grasp the bar with an overhand grip, with your hands close together (typically 6-8 inches apart). Position yourself: Stand up straight, close to the machine. Let the bar hang in front of your thighs with your arms extended. Pull: Exhale and pull the bar straight up towards your chin. Lead with your elbows, keeping them high and out to the sides. Squeeze at the top: Pause when the bar reaches your upper chest or chin. Your elbows should be higher than your hands. Squeeze your traps and shoulders. Lower with control: Inhale and slowly lower the bar back down to the starting position. Repeat: Repeat the exercise, keeping your torso stable. Coach Tips: Keep the bar close to your body throughout the entire lift. Lead with your elbows; they should always be the highest point of your arms. Avoid using momentum or leaning back to lift the weight.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Captains Chair Knee Raise',
    'CaptainsChairKneeRaise.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Captains Chair Knee Raise Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Position yourself: Stand in the Captain''s Chair and place your forearms firmly on the pads. Grip the handles. Press your back: Press your lower back firmly against the back pad. Your legs should be hanging straight down. Engage your core: Brace your abdominal muscles. Raise your knees: Exhale and slowly lift your knees up towards your chest. Aim for at least a 90-degree angle at your hips. Squeeze your abs: Pause for a moment at the top and squeeze your abs hard. Lower with control: Slowly and with control, inhale as you lower your legs back to the starting position. Do not let them just drop. Repeat: Repeat the exercise, ensuring your back stays pressed against the pad. Coach Tips: Do not use momentum or "swing" your legs up. The movement must be controlled and initiated by your abs. The most important part is pressing your lower back into the pad. If it arches, you are not using your abs effectively. For a greater challenge, try to keep your legs straight (Straight Leg Raise), but only if you can do so without your back arching.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dead Bug',
    'DeadBug.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dead Bug Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Starting position: Lie flat on your back. Lift your arms straight up towards the ceiling (perpendicular to the floor). "Tabletop" legs: Lift your legs so your knees are bent at a 90-degree angle, with your shins parallel to the floor (the "tabletop" position). Engage core: Actively press your entire lower back into the floor. There should be no gap. Extend opposites: Slowly extend your right arm straight back behind your head while simultaneously extending your left leg straight out. Lower both until they are just above the floor. Maintain contact: Exhale as you extend, and keep your lower back pressed firmly into the floor. Return to start: Slowly bring your right arm and left leg back to the starting "tabletop" position. Repeat (other side): Repeat the movement with your left arm and right leg. This completes one rep. Coach Tips: The number one rule is: Do not let your lower back arch off the floor. If it does, you are extending too far. This exercise is about control, not speed. Move slowly and deliberately. Exhale on the extension and inhale on the return. This helps you keep your core braced.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Diagonal Plank',
    'DiagonalPlank.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Diagonal Plank Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Start in plank: Begin in a high plank position (on your hands) with hands under shoulders and feet hip-width apart. Your body should be a straight line. Brace your core: Engage your abs and glutes to create a stable, rigid torso. Widen your feet slightly for a more stable base. Lift right arm: Slowly lift your right arm straight out in front of you, parallel to the floor. Lift left leg: Simultaneously, slowly lift your left leg straight back, parallel to the floor. Hold and stabilize: Hold this "diagonal" position for 2-5 seconds. Your main goal is to keep your hips completely level and square to the floor. Return to start: Slowly and with control, lower your arm and leg back to the plank position. Repeat (other side): Repeat the movement by lifting your left arm and right leg. Coach Tips: The goal is to prevent all rotation. Imagine you have a glass of water on your lower back that you can''t spill. If this is too difficult, start by lifting just one arm, then just one leg. Build up to lifting both. Keep your neck in line with your spine; don''t look up or let your head sag.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Bench Fly',
    'DumbbellBenchFly.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Bench Fly Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Select dumbbells: Choose two dumbbells of a moderate weight (lighter than your bench press). Position yourself: Lie flat on your back on a bench. Plant your feet firmly on the floor. Starting position: Press the dumbbells up and hold them over your chest, palms facing each other. Keep a slight, constant bend in your elbows (like you''re hugging a large tree). Lower (Fly): Inhale and slowly lower the dumbbells out to your sides in a wide, sweeping arc. Feel the stretch: Lower the weights until they are level with your chest and you feel a good stretch in your pecs. Do not drop your elbows below your shoulders. Squeeze together: Exhale and reverse the motion, "hugging" the tree to bring the dumbbells back together over your chest. Squeeze your pecs hard at the top. Repeat: Repeat the movement, ensuring you keep the bend in your elbows constant. Coach Tips: This is a "fly," not a "press." Do not bend or straighten your elbows during the rep; keep them slightly bent. Keep your shoulders "packed" (down and back) into the bench. Do not let them roll forward. Control the weight, especially on the way down. Do not over-stretch your shoulders.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Bench One Arm Tricep Kickback',
    'DumbbellBenchOneArmTricepKickback.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Bench One Arm Tricep Kickback Exercise for Tricep</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Position yourself: Place one knee and the same-side hand on a flat bench (e.g., left knee, left hand). Your torso should be parallel to the floor. Grip the dumbbell: Hold a dumbbell in your opposite (right) hand with a neutral grip (palm facing in). Set your arm: Lift your right arm so your upper arm (tricep) is parallel to the floor and "pinned" to your side. Your elbow should be bent at 90 degrees. This is your starting position. Extend: Exhale and, keeping your upper arm stationary, extend your arm straight back, using your tricep. Squeeze your tricep: Pause at the top when your arm is fully straight and squeeze your tricep hard. Return with control: Inhale and slowly lower the dumbbell back to the 90-degree starting position. Repeat: Complete all repetitions on one arm before switching sides. Coach Tips: The most important rule: Your upper arm must stay parallel to the floor and locked in place. Only your forearm should move. Avoid using momentum or "swinging" the weight. This is a strict isolation exercise. A full contraction at the top is key.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Bench Press',
    'DumbbellBenchPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Bench Press Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Select dumbbells: Choose two dumbbells of appropriate weight. Position yourself: Sit on the edge of a flat bench with the dumbbells resting on your knees. "Kick" your knees up one at a time to help you lie back and bring the dumbbells to the starting position. Starting position: Lie flat on your back. The dumbbells should be held at the sides of your chest, with your palms facing forward and your elbows tucked at about a 45-degree angle. Press: Exhale and push the dumbbells straight up and slightly in, so they meet over the center of your chest. Squeeze at the top: Squeeze your chest, shoulders, and triceps at the top, but do not lock out your elbows. Lower with control: Inhale and slowly lower the dumbbells back down to the starting position at the sides of your chest. Repeat: Repeat the movement for the desired number of repetitions. Coach Tips: Keep your feet planted firmly on the floor and your glutes/upper back glued to the bench. Control the descent (lowering) phase. Don''t let the dumbbells just drop. Tucking your elbows (not flaring them out to 90 degrees) is safer for your shoulder joints and engages the pecs effectively.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Bicep Curl',
    'DumbbellBicepCurl.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Bicep Curl Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Select dumbbells: Choose a pair of dumbbells of appropriate weight. Position yourself: Stand tall (or sit on a bench) with your chest up and shoulders back. Grip the dumbbells: Hold the dumbbells at your sides with your arms fully extended. Your palms should be facing forward (a supinated grip). Curl: Exhale and, keeping your elbows "pinned" to your sides, curl both dumbbells up towards your shoulders. Squeeze your bicep: Pause at the top of the movement and squeeze your biceps hard. Lower with control: Inhale and slowly lower the dumbbells back to the starting position, keeping tension on the muscle. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Do not use momentum or "swing" your body to lift the weight. Keep your elbows stationary at your sides; do not let them drift forward. Control the negative (lowering) phase; don''t just let the weights drop.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Bicep Curl Alternating',
    'DumbbellBicepCurlAlternating.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Bicep Curl Alternating Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Position yourself: Stand or sit tall with your chest up and shoulders back. Hold a dumbbell in each hand, palms facing forward (supinated grip) or facing your body (neutral grip). Starting position: Your arms should be fully extended at your sides. Curl (Right arm): Exhale and curl the right dumbbell up towards your right shoulder. Keep your elbow pinned to your side. (If starting neutral, rotate your palm to face up as you curl). Squeeze: Squeeze your bicep at the top of the movement. Lower (Right arm): Inhale and slowly lower the right dumbbell back to the starting position. Curl (Left arm): As the right dumbbell returns, begin to curl the left dumbbell up towards your left shoulder, repeating the motion. Repeat: Continue alternating arms for the desired number of repetitions. Coach Tips: Keep your elbows locked at your sides. Do not let them swing forward or back. Avoid using momentum or swinging your body. Keep your torso stable. Control the negative (lowering) phase of each rep; don''t just let the dumbbell drop.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Incline Bicep Curl',
    'DumbbellInclineBicepCurl.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Incline Bicep Curl Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the bench: Set an incline bench to a 45 or 60-degree angle. Position yourself: Sit back on the bench, planting your feet firmly on the floor. Your chest should be up and your shoulders back. Grip and start: Hold a dumbbell in each hand, letting your arms hang straight down. Your palms should face in (neutral grip) or slightly forward. Curl: Exhale and curl the dumbbells up towards your shoulders. As you curl, rotate your wrists (supinate) so your palms face you at the top. Squeeze your bicep: Pause at the top and squeeze your biceps, keeping your upper arms stationary. Lower with control: Inhale and slowly lower the dumbbells back to the starting position, allowing your arms to fully extend and get a deep stretch. Repeat: Repeat the movement for the desired number of repetitions. Coach Tips: Keep your elbows "pinned" and pointing down. Do not let them drift forward as you curl. The incline position provides a unique stretch; take advantage of the full range of motion. Keep your head and back pressed against the bench.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Lying Tricep Extension',
    'DumbbellLyingTricepExtension.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Lying Tricep Extension Exercise for Tricep</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Position the bench: Lie flat on your back on a bench. Plant your feet firmly on the floor. Grip the dumbbells: Hold one dumbbell in each hand and press them up so your arms are fully extended over your chest. Starting position: Your palms should be facing each other (a neutral grip). Keep your upper arms vertical and stationary. Lower the weight: Inhale and slowly bend only at your elbows, lowering the dumbbells down towards your ears or the sides of your head. Extend: Exhale and press the dumbbells back up to the starting position by extending your elbows. Squeeze your tricep: Squeeze your triceps hard at the top (lockout) position. Repeat: Repeat the movement, keeping your upper arms still throughout. Coach Tips: Your upper arms should not move. Keep them perpendicular to the floor. All movement should be from the elbow joint. Do not let your elbows flare out excessively; try to keep them tucked. Control the descent; do not let the dumbbells drop too fast.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Overhead One Arm Tricep Extension',
    'DumbbellOverheadOneArmTricepExtension.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Overhead One Arm Tricep Extension Exercise for Tricep</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Position yourself: Sit on a bench (preferably with back support) or stand tall. Hold a single dumbbell in one hand. Grip the dumbbell: Raise the dumbbell overhead so your arm is fully extended. Starting position: Use your non-working hand to support your working elbow or brace it against your torso. Lower the weight: Inhale and slowly bend at your elbow, lowering the dumbbell behind your head. Keep your bicep/upper arm close to your head. Extend: Exhale and press the dumbbell back up to the starting position by extending your elbow. Squeeze your tricep: Squeeze your tricep hard at the top of the movement. Repeat: Complete all repetitions on one arm before switching to the other. Coach Tips: Keep your upper arm vertical and close to your head. Do not let your elbow flare out to the side. Brace your core to prevent your lower back from arching, especially when standing. Focus on getting a deep stretch at the bottom and a full contraction at the top.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Overhead Weighted Sit Up',
    'DumbbellOverheadWeightedSitUp.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Overhead Weighted Sit Up Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Position yourself: Lie flat on your back on the floor. Bend your knees and plant your feet firmly. Grip the dumbbell: Hold a single dumbbell with both hands (by the ends, "goblet" style) or one in each hand. Starting position: Extend your arms straight up, holding the dumbbell directly over your chest. Sit up: Exhale, brace your core, and "punch" the dumbbell toward the ceiling as you perform a full sit-up. Pause at the top: At the top, you should be sitting tall, with the dumbbell held overhead and arms fully extended. Lower with control: Inhale and slowly roll your spine back down to the floor, vertebra by vertebra, keeping your arms extended. Repeat: Repeat the movement for the desired number of repetitions. Coach Tips: Keep your arms locked straight throughout the entire movement. If your feet lift, you can "anchor" them under a stable object. Focus on "punching" the weight straight up to the ceiling to help guide the movement.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Seated Lateral Raise',
    'DumbbellSeatedLateralRaise.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Seated Lateral Raise Exercise for Shoulders</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Select dumbbells: Choose a pair of light dumbbells. This is an isolation exercise, so form is more important than weight. Position yourself: Sit on the edge of a flat bench with your feet planted firmly on the floor. Keep your chest up and back straight. Grip and start: Hold the dumbbells at your sides with your palms facing your body (neutral grip). Your arms should have a slight, constant bend in the elbows. Raise: Exhale and, keeping the slight bend in your elbows, raise the dumbbells out to your sides in a wide arc. Squeeze at the top: Continue lifting until your arms are parallel to the floor. Pause and squeeze your side deltoids (shoulders). Lower with control: Inhale and slowly lower the dumbbells back down to your sides in a controlled manner. Repeat: Repeat the movement, avoiding any rocking or momentum from your torso. Coach Tips: Lead the movement with your elbows, not your hands. Imagine you are pouring two jugs of water, with your pinky finger slightly higher than your thumb. Do not shrug your shoulders (traps) up towards your ears. Keep your shoulders down and relaxed. Sitting on a bench helps prevent you from using your legs to "cheat" the weight up.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'High Knee Taps Cardio',
    'HighKneeTapsCardio.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing High Knee Taps Cardio Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Start standing: Stand tall with your feet hip-width apart. Keep your chest up and core engaged. Hands out (optional): Hold your hands out in front of you, palms facing down, at hip or belly-button height. Drive right knee: Explosively drive your right knee up towards your chest, aiming to tap your palm. Drive left knee: As your right foot returns to the floor, immediately drive your left knee up towards your chest to tap your other palm. Alternate: Continue alternating legs at a fast, rhythmic, "running-in-place" pace. Stay on toes: Stay light on your feet, landing on the balls of your feet, not your heels. Repeat: Continue this alternating motion for the desired duration or number of repetitions. Coach Tips: Focus on lifting your knees high; the work comes from driving the knee up, not just "kicking" your foot. Keep your torso upright and core braced. Avoid leaning back as you lift your knees. Use your arms in a running motion if you are not tapping your hands to help drive the intensity.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Chest Press',
    'LeverChestPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Chest Press Exercise for Chest</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the machine: Adjust the seat height so that the handles are in line with the middle of your chest. Position yourself: Sit down with your back pressed firmly against the back pad. Plant your feet on the floor. Grip the handles: Grasp the handles with your preferred grip (usually horizontal or neutral). Your elbows should be slightly below your shoulders. Press: Exhale and press the handles forward until your arms are fully extended, but not locked out. Squeeze your chest muscles. Pause and squeeze: Pause for a moment and focus on the chest contraction. Return with control: Inhale and slowly bring the handles back towards your chest. Allow a good stretch, but stop before the weights "clank". Repeat: Repeat the exercise, keeping your back and glutes pressed against the pads. Coach Tips: Do not let your shoulders roll forward or lift off the pad. Keep them pulled back and down. Control the negative (return) phase. Don''t let the weight stack slam. Focus on a "mind-muscle connection" – think about your chest muscles doing the work, not your shoulders or triceps.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Crunch',
    'LeverCrunch.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Crunch Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Set the seat height so the pads rest comfortably on your upper shoulders or chest. Select your desired weight. Position yourself: Sit in the machine and place your feet under the foot rollers (if available). Grasp the handles or place your hands on the pads. Starting position: Sit upright with your abs lightly engaged. Crunch: Exhale and contract your abdominal muscles to "curl" your torso forward and down. Squeeze your abs: Focus on bringing your rib cage toward your pelvis. Pause at the bottom and squeeze your abs hard. Return with control: Inhale and slowly return to the starting position. Do not let the weight stack slam. Repeat: Repeat the movement, ensuring the work is done by your abs, not by pulling with your arms or neck. Coach Tips: The movement should be a spinal "curl," not a hip hinge. Your lower back should stay in contact with the pad. Do not pull with your arms or neck. Your arms are just there to hold the pads in place. Exhale forcefully as you crunch to get a deeper abdominal contraction.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Lateral Raise',
    'LeverLateralRaise.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Lateral Raise Exercise for Shoulders</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Adjust the seat height so the pivot point of the machine (the axle) is in line with your shoulder joint. Position yourself: Sit down and place your arms against the pads. Your elbows should be slightly bent, and the pads should rest on your upper arms or just above your elbows. Grip the handles (optional): Lightly grip the handles. The work should not come from your hands. Raise: Exhale and lead with your elbows, raising your arms out to your sides until they are parallel to the floor (or in line with your shoulders). Squeeze at the top: Pause for a moment at the top and focus on the contraction in your side deltoids (shoulders). Lower with control: Inhale and slowly lower the pads back down to the starting position. Do not let the weight stack slam. Repeat: Repeat the movement, keeping your chest up and back pressed against the pad. Coach Tips: Lead with your elbows, not your hands. Think about pushing your elbows out and up. Do not shrug your shoulders (traps) up towards your ears. Keep your shoulders down and focus the work on the middle deltoid. Keep your torso stable and pressed against the back pad. Do not use momentum to swing the weight.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Leg Extension',
    'LeverLegExtension.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Leg Extension Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Adjust the back pad so your knees are bent 90 degrees and the back of your knees are flush with the edge of the seat. Adjust the ankle pad so it rests on your lower shin, just above your ankles. Position yourself: Sit in the machine and grasp the support handles on the side. Starting position: Your knees should be bent to 90 degrees. Extend your legs: Exhale and fully extend your legs, using your quadriceps (thigh muscles). Squeeze at the top: Pause at the top of the movement and squeeze your quads hard for a second. Lower with control: Inhale and slowly lower the weight back down to the 90-degree starting position. Repeat: Repeat the exercise, avoiding letting the weight stack "slam" at the bottom. Coach Tips: Do not use momentum. The movement should be controlled, especially the lowering (eccentric) phase. Squeeze your quads at the top of the movement. This is the most important part of the exercise. Keep your hips and glutes planted in the seat. Do not let them rise up as you extend your legs.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Lying Leg Curl',
    'LeverLyingLegCurl.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Lying Leg Curl Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Adjust the machine so the pivot point (axle) is in line with your knee joint. Adjust the ankle pad so it rests just above your heels on your Achilles tendon. Position yourself: Lie face down on the machine. Grasp the support handles in front of you. Starting position: Your legs should be fully extended with the pad resting on your lower ankles. Curl: Exhale and curl your legs, pulling your heels as close to your glutes as possible. Squeeze at the top: Pause at the top and squeeze your hamstrings hard. Lower with control: Inhale and slowly lower the pad back to the starting position, resisting the weight as you extend. Repeat: Repeat the movement, keeping your hips pressed into the pad. Coach Tips: Keep your hips pressed firmly into the bench pad throughout the entire set. Do not let your hips rise up as you curl. Control the lowering phase. Don''t just let the weight drop; this is a key part of the exercise. Focus on pulling with your hamstrings, not your lower back.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Pec Deck',
    'LeverPecDeck.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Pec Deck Exercise for Chest</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Adjust the seat height so that the handles are in line with the middle of your chest. Position yourself: Sit down with your back pressed firmly against the back pad. Position your arms: Place your forearms against the pads (if it''s a "pad" machine) or grasp the handles (if it''s a "handle" machine). Your elbows should be slightly bent (10-15 degrees). Bring handles together: Exhale and slowly bring the handles (or pads) together in a wide arc, as if you are "hugging a tree." Squeeze your chest: Pause for a moment when the handles meet and squeeze your chest muscles hard. Return to start: Inhale and slowly reverse the motion, letting the handles go back to the starting position. Feel a stretch in your chest, but don''t go past a comfortable range of motion. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Keep a slight, constant bend in your elbows. Do not let them straighten or bend more during the rep. Keep your shoulders back and down, pressed against the back pad. Do not let your shoulders roll forward. The work should be felt 100% in your chest, not your front shoulders.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Pulldown',
    'LeverPulldown.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Pulldown Exercise for Back</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Adjust the knee pad so it locks your thighs down firmly when you are seated. Grip the bar: Stand up and grasp the pulldown bar with a wide, overhand grip. Position yourself: Sit down, pulling the bar with you, and secure your knees under the pad. Your feet should be flat on the floor. Starting position: Lean back slightly (10-15 degrees) with your chest up and arms fully extended. Pull: Exhale and drive your elbows down and back, pulling the bar towards your upper chest (collarbone). Squeeze at the bottom: Pause and squeeze your shoulder blades together and down, contracting your back muscles (lats). Return with control: Inhale and slowly let the bar return to the starting position, allowing your lats to stretch fully. Repeat. Coach Tips: Think of "pulling with your elbows," not your hands. This helps engage your lats instead of your biceps. Keep your chest up and out. Do not round your shoulders or use your torso to "swing" the weight down. Control the upward (eccentric) phase. Don''t let the weight stack "yank" you back up.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Seated Leg Curl',
    'LeverSeatedLegCurl.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Seated Leg Curl Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the machine: Adjust the back pad so your knee joint aligns perfectly with the machine''s pivot point. Adjust the leg pad so it rests just above your heels on your Achilles tendon. Position yourself: Sit in the machine with your back firmly against the pad. Secure the thigh pad so it locks your legs in place. Grasp handles: Grasp the support handles on the side to keep your body stable. Curl: Exhale and curl your legs, pulling your heels back and under the seat as far as possible. Squeeze at the top: Pause at the peak of the contraction and squeeze your hamstrings hard. Lower with control: Inhale and slowly return the pad to the starting position, resisting the weight as your legs extend. Do not let the weight stack slam. Repeat: Repeat the movement, keeping your hips and back planted in the seat. Coach Tips: Ensure your knee is aligned with the machine''s pivot point; this is crucial for correct form and knee safety. Keep your hips and glutes from lifting off the seat. Use the handles to brace yourself. Control the entire movement, especially the slow, negative (lowering) phase.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lever Standing Calf Raise',
    'LeverStandingCalfRaise.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lever Standing Calf Raise Exercise for Calves</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Adjust the shoulder pads so they rest comfortably on your shoulders when you are standing with your knees slightly bent. Position yourself: Stand on the platform with the balls of your feet on the edge, leaving your heels free to move. Place your shoulders under the pads. Starting position: Stand up straight by extending your legs, lifting the weight. Your heels should be in a "neutral" or slightly dropped position for a full stretch. Raise your heels: Exhale and push through the balls of your feet, raising your heels as high as possible. Squeeze at the top: Pause at the top of the movement and squeeze your calf muscles hard for 1-2 seconds. Lower with control: Inhale and slowly lower your heels back down, going below the platform level until you feel a deep stretch in your calves. Repeat: Repeat the movement for the desired number of repetitions. Coach Tips: Keep your knees straight (but not hyper-extended) throughout the entire movement to target the gastrocnemius (upper calf). The "pause and squeeze" at the top and the "deep stretch" at the bottom are the most important parts of the exercise. Avoid "bouncing" the weight. Use a smooth, controlled tempo.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Lying Leg Raise',
    'LyingLegRaise.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Lying Leg Raise Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Lie on your back: Lie flat on your back. You can place your hands under your lower back/glutes for support, or by your sides. Legs straight: Extend your legs straight out, feet together. Press back: Actively press your lower back into the floor (or into your hands). This is crucial. Raise your legs: Exhale and slowly raise both legs, keeping them straight, until they are perpendicular to the floor (or as high as you can). Squeeze your abs: Pause at the top. Lower with control: Inhale and slowly lower your legs back down towards the floor. Stop just before they touch the ground to maintain tension. Repeat: Repeat the movement without letting your lower back arch off the floor. Coach Tips: Your number one priority is to keep your lower back pressed into the floor. If it arches, you are using your back, not your abs. If this is too hard, you can bend your knees slightly. The slower and more controlled you perform the lowering phase, the more effective the exercise will be for your lower abs.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Pendulum Squat',
    'PendulumSquat.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Pendulum Squat Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Position yourself: Step into the pendulum squat machine. Place your shoulders firmly under the pads and your back flat against the back pad. Set your feet: Place your feet on the platform, typically shoulder-width apart and slightly high on the platform to target glutes/hams, or lower to target quads. Starting position: Straighten your legs to support the weight and release the safety handles. Keep a slight bend in your knees. Squat down: Inhale and slowly lower your body by bending your knees and hips. The machine''s arc will guide your movement. Hit depth: Lower until your thighs are at least parallel to the platform, or as deep as your mobility allows. Drive up: Exhale and drive through your entire foot (especially your heels) to push the weight back up to the starting position. Squeeze your quads and glutes at the top. Repeat: Repeat the movement, keeping your back pressed against the pad at all times. Coach Tips: This machine provides excellent back support. Use this to your advantage and focus on pushing with your legs. Do not lock out your knees aggressively at the top; keep constant tension. Keep your entire back, from your hips to your shoulders, pressed against the pad throughout the lift.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Plank Jack Cardio',
    'PlankJackCardio.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Plank Jack Cardio Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Start in plank: Begin in a high plank position, with your hands directly under your shoulders, arms straight. Your body should form a straight line from head to heels. Feet together: Start with your feet touching each other. Jump feet out: Keeping your core braced and upper body still, jump both feet out wide (wider than shoulder-width). Jump feet in: Immediately jump both feet back together to the starting position. Maintain form: The movement should only be in your lower body. Do not let your hips bounce up and down. Keep core tight: Your primary focus is to keep your core engaged and prevent your lower back from sagging. Repeat: Repeat the "out-in" jack motion at a quick, steady pace for the desired time. Coach Tips: Do not let your hips pike up into the air. Keep them in line with your shoulders. If jumping is too high-impact, you can modify this by stepping one foot out to the side at a time (a "Plank Step-Out"). Keep your shoulders "active" by pushing the ground away from you; don''t sink into your shoulder blades.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Plate Weighted Back Extension',
    'PlateWeightedBackExtension.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Plate Weighted Back Extension Exercise for Lower Back and Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the bench: Set the pad of the hyperextension bench so it rests just below your hip bones, allowing you to hinge freely. Position yourself: Secure your ankles or heels under the foot pads. Hold a weight plate firmly against your chest with both hands. Starting position: Hinge at your hips and lower your torso down, keeping your back straight (not rounded). Lower as far as your hamstring flexibility allows. Raise your torso: Squeeze your glutes and lower back muscles to lift your torso back up. Squeeze at the top: Continue lifting until your body forms a straight, solid line from your head to your heels. Pause briefly and squeeze your glutes. Return to start: Slowly and with control, lower your torso back down to the starting position. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Avoid hyperextending (arching) your back at the top. Your body should form a straight line, not a "C" shape. Keep your neck in a neutral position, in line with your spine. Do not look up at the ceiling. The movement should be a "hinge" from the hips, driven by your glutes and hamstrings, not by rounding your upper back.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Rowing',
    'Rowing.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Rowing Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Set your feet: Sit on the rower and secure your feet in the straps. The straps should be tight across the widest part of your foot (the ball). The "Catch" (Start): Grab the handle with an overhand grip. Slide forward until your shins are vertical. Your arms are straight, and your back is straight (hinged forward from the hips). The "Drive" (Legs): Explode by pushing with your legs. This is the first and most powerful part of the stroke. The "Swing" (Body): As your legs straighten, lean your torso back slightly (to about an 11 o''clock position). The "Pull" (Arms): Once your body is leaned back, use your arms to pull the handle to your lower chest / upper abdomen. The "Recovery": Reverse the order: 1) Extend your arms. 2) Hinge your torso forward. 3) Bend your knees and slide back to the "Catch." Repeat: Repeat this "Legs -> Body -> Arms -> Arms -> Body -> Legs" sequence for a fluid, powerful stroke. Coach Tips: The power comes from your legs (about 60%), not your arms. Think "Push" with your legs, not "Pull" with your arms. Maintain a straight, "proud" chest and a flat back. Do not round your lower back. The "Recovery" (sliding forward) should be slow and controlled, about twice as long as the "Drive" (pulling back).'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Running Plank Cardio',
    'RunningPlankCardio.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Running Plank Cardio Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Start in plank: Begin in a high plank position with your hands directly under your shoulders and your body in a straight line from head to heels. Brace your core: Actively engage your core and glutes to keep your hips stable and low. Drive right knee: Explosively drive your right knee toward your chest, as if you are running. Return right foot: Quickly return your right foot back to the starting plank position. Drive left knee: As your right foot lands, immediately drive your left knee toward your chest. Return left foot: Quickly return your left foot to the starting plank position. Repeat: Continue alternating knees at a rapid, rhythmic pace, like running in place. Coach Tips: Your primary focus is to keep your hips from bouncing up and down. Your upper body should remain stable. Keep your core tight to prevent your lower back from sagging. Stay on the balls of your feet to allow for quick transitions.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Seated Lever Hip Abduction',
    'SeatedLeverHipAbduction.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Seated Lever Hip Abduction Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Sit in the machine and adjust the pads/levers. The pads should be on the outside of your knees or upper thighs. Position yourself: Sit with your back firmly against the pad. Grasp the support handles. Starting position: Your legs should be together, with the pads resting against them. Push out: Exhale and use your outer thighs and glutes (gluteus medius) to push your legs apart, driving against the pads. Squeeze at the top: Push out as far as you can, pause, and squeeze your glutes. Return with control: Inhale and slowly bring your legs back together, resisting the weight. Do not let the weight stack slam. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: You can lean forward slightly at the hips to target the gluteus medius more effectively. Control the return (adduction) phase. Don''t let your legs snap shut. Focus on pushing "out" with the sides of your legs/glutes, not just spreading your knees.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Seated Lever Hip Adduction',
    'SeatedLeverHipAdduction.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Seated Lever Hip Adduction Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Sit in the machine and adjust the pads/levers. The pads should be on the inside of your knees or lower thighs. Position yourself: Sit with your back firmly against the pad. Grasp the support handles. Starting position: Use the lever (if available) or your hands to position your legs open to a comfortable stretch. Squeeze in: Exhale and use your inner thigh muscles (adductors) to squeeze your legs together. Squeeze at the center: Pause for a moment when the pads touch and squeeze your inner thighs hard. Return with control: Inhale and slowly let your legs return to the starting (open) position, resisting the weight. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Control the return (eccentric) phase. Do not let your legs "snap" open; resist the weight. Keep your back pressed firmly against the pad. Do not use momentum. Focus on a strong, deliberate squeeze from your inner thighs on every repetition.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Side Bridge',
    'SideBridge.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Side Bridge Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Lie on your side: Lie on your side with your legs straight and stacked one on top of the other. Position your elbow: Place your forearm on the floor, ensuring your elbow is directly underneath your shoulder. Engage your core: Brace your abdominal muscles. Lift your hips: Exhale and lift your hips off the floor, supporting your weight on your elbow and the side of your foot. Form a straight line: Your body should form a straight, rigid line from your head to your ankles. Do not let your hips sag. Hold: Hold this position for the desired duration, breathing steadily. Repeat (other side): Slowly lower your hips back to the floor and repeat the exercise on the opposite side. Coach Tips: Keep your neck in line with your spine; don''t let your head drop. Actively push your hips up toward the ceiling to keep them from sagging. If this is too difficult, you can modify by bending your knees 90 degrees and lifting from your knees instead of your feet.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Sit Up',
    'SitUp.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Sit Up Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Lie on your back: Lie flat on your back with your knees bent and your feet flat on the floor, about hip-width apart. Position your hands: You can place your hands lightly behind your head (do not pull!) or cross them over your chest. Engage your core: Take a breath and brace your core. Lift your torso: Exhale and curl your entire torso up off the floor, leading with your chest, until you are in a seated position. Squeeze at the top: Pause briefly in the upright position. Lower with control: Inhale and slowly roll your spine back down onto the floor, one vertebra at a time, to the starting position. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: If your feet lift off the floor, "anchor" them under a dumbbell or piece of furniture, or have a partner hold them. Focus on "curling" your spine up and down. Avoid a stiff, "board-like" movement that relies on your hip flexors. Control the descent; don''t just flop back down. The eccentric (lowering) phase is just as important.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Sled Leg Press',
    'SledLegPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Sled Leg Press Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the seat: Sit in the leg press machine and adjust the back pad angle for comfort (most prefer a slightly reclined position). Position your feet: Place your feet on the sled platform, typically shoulder-width apart. (Higher on the platform targets glutes/hams; lower targets quads). Starting position: Push the weight up to extend your legs (do not lock them) and release the safety handles. Lower the weight: Inhale and slowly lower the sled by bending your knees. Lower until your knees form a 90-degree angle or as deep as your mobility allows. Press: Exhale and drive through your heels and mid-foot to push the sled back up to the starting position. Squeeze at the top: Squeeze your quads and glutes at the top, but avoid "locking out" your knees. Repeat: Repeat the movement, keeping the tension on your legs. Coach Tips: Crucial: Keep your lower back and glutes pressed into the seat pad at all times. Do not let your lower back round or your hips lift off the pad (this is dangerous). Control the descent. Do not let the weight "drop" and bounce at the bottom. Drive through your heels to engage your glutes and hamstrings more effectively.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Smith Bench Press',
    'SmithBenchPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Smith Bench Press Exercise for Chest</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set the bench: Position a flat bench in the center of the Smith machine. Set the safety stoppers at a height just above your chest. Lie on the bench: Lie flat on the bench so the bar is aligned directly over your mid-chest. Plant your feet firmly on the floor. Grip the bar: Grasp the bar with an overhand grip, slightly wider than shoulder-width. Unrack: Rotate the bar to unhook it from the machine. Start with your arms fully extended. Lower the bar: Slowly lower the bar with control until it lightly touches your mid-chest. Keep your elbows tucked slightly. Press: Explosively press the bar straight back up to the starting position, extending your elbows and squeezing your chest. Repeat: Repeat for the desired number of repetitions. When finished, re-rack the bar by rotating your wrists. Coach Tips: The Smith machine forces a fixed vertical path, so focus on your pressing power and controlling the negative (lowering) phase. Keep your shoulder blades retracted and "screwed" into the bench, just as you would with a regular barbell. Do not bounce the bar off your chest. Use the safety stoppers to control the range of motion if needed.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Smith Bent Over Row',
    'SmithBentOverRow.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Smith Bent Over Row Exercise for Back</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set the bar: Set the Smith machine bar to a height just below your knees. Stand with your feet shoulder-width apart. Grip the bar: Hinge at your hips and bend your knees slightly, keeping your back straight (nearly parallel to the floor). Grasp the bar with an overhand, shoulder-width grip. Unrack: Unhook the bar by rotating it. The bar should be hanging on straight arms. Row: Keeping your torso stationary, exhale and pull the bar up towards your lower chest/upper abdomen. Squeeze your shoulder blades together. Squeeze at the top: Pause briefly at the top of the movement, focusing on the contraction in your back. Lower with control: Inhale and slowly lower the bar back to the starting position, maintaining your straight back. Repeat: Repeat the exercise for the desired number of repetitions. Re-rack the bar when finished. Coach Tips: Maintaining a flat, neutral spine is the most important part of this exercise. Do not round your back. Your torso should remain rigid. Avoid using "body English" or momentum to lift the weight. Pull with your elbows and back, not just your biceps.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Smith Bulgarian Split Squat',
    'SmithBulgarianSplitSquat.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Smith Bulgarian Split Squat Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set up: Place a bench a few feet behind the Smith machine. Set the bar on your shoulders/upper back, as you would for a squat. Position your feet: Stand in a split stance. Place your front foot on the floor directly under the bar and your back foot (shoelaces down) on the bench behind you. Unrack: With the bar on your back, unhook it from the machine. Find your balance. Squat down: Inhale and lower your body straight down, bending your front knee. Lower until your front thigh is at least parallel to the floor. Drive up: Exhale and drive through your front heel to push yourself back up to the starting position. Maintain form: Keep your chest up and your core engaged throughout the movement. Repeat: Complete all repetitions for one leg before switching to the other leg. Coach Tips: Your front knee should track in line with your front foot; do not let it collapse inward. The bar path is fixed, so your foot placement is key. Adjust your front foot forward or backward until the movement feels smooth and stable. Focus the work on your front leg''s quad and glute.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Smith Deadlift',
    'SmithDeadlift.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Smith Deadlift Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set the bar: Set the Smith machine bar to a low position, typically mid-shin height. Set the safety stoppers just below this. Position your feet: Stand with your feet hip-width apart, with your shins very close to the bar. Grip the bar: Hinge at your hips and bend your knees. Grasp the bar with an overhand grip just outside your legs. Keep your back straight, chest up, and core braced. Lift: Exhale, drive through your heels, and lift the bar by straightening your legs and hips simultaneously. Pull your shoulders back at the top. Squeeze at the top: Stand tall and squeeze your glutes hard. Do not lean back. Lower with control: Inhale, hinge at your hips first, then bend your knees to lower the bar back down to the starting position. Keep your back straight. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: The Smith machine forces a vertical path, which is different from a free-weight deadlift. Focus on keeping your back flat. Keep the bar as close to your body as possible (though the machine guides this). The lift should be driven by your legs and glutes, not by pulling with your lower back.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Smith Front Squat',
    'SmithFrontSquat.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Smith Front Squat Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set the bar: Set the bar in the Smith machine at shoulder height. Grip the bar: Position the bar across your front shoulders (deltoids). Use either a "clean grip" (hands under the bar, elbows high) or a "crossed-arm" grip (hands crossed, holding the bar on your shoulders). Unrack: Stand up to unhook the bar. Place your feet shoulder-width apart, toes slightly out. Squat down: Inhale and push your hips back, then bend your knees to lower your body. Keep your chest up and elbows high. Hit depth: Lower until your hips are at least parallel to the floor, or as low as your mobility allows. Drive up: Exhale and drive through your heels to return to the standing position, squeezing your glutes at the top. Repeat: Repeat the exercise for the desired number of repetitions. Coach Tips: Keeping your elbows high is critical. If they drop, your upper back will round, and you may lose the bar. The fixed path allows you to focus on a very upright torso, which targets the quads heavily. Keep your core braced and tight throughout the entire squat.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Smith Good Morning',
    'SmithGoodMorning.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Smith Good Morning Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Set the bar: Set the Smith machine bar at shoulder height, just like a squat. Position the bar: Place the bar across your upper back/traps (not on your neck). Stand with feet shoulder-width apart. Unrack: Unhook the bar. Keep a slight, soft bend in your knees. Hinge forward: Inhale and begin the movement by pushing your hips backward. Hinge forward at your hips, keeping your back perfectly straight. Lower your torso: Lower your torso until it is nearly parallel to the floor, or until you feel a strong stretch in your hamstrings. Return to start: Exhale, squeeze your glutes and hamstrings, and push your hips forward to pull your torso back up to the standing position. Repeat: Repeat the exercise, focusing on the hip hinge. Coach Tips: This exercise is all about the hip hinge, not squatting. Your shins should remain almost vertical. Start with very light weight. This exercise can put stress on the lower back if done incorrectly. The key is to keep your back flat (neutral spine) from your head to your tailbone. Do not round your back.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Smith Hip Thrust',
    'SmithHipThrust.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Smith Hip Thrust Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set up: Place a flat bench parallel to the Smith machine bar. Set the bar height so it rests in your hip crease when you are seated on the floor with your upper back against the bench. Position yourself: Sit on the floor, lean your upper back (just below the shoulder blades) against the bench. Roll the bar over your legs so it sits directly in your hip crease. (A pad on the bar is recommended). Set your feet: Plant your feet flat on the floor, shoulder-width apart, with knees bent. Your shins should be roughly vertical at the top of the movement. Unrack: Grasp the bar with your hands to stabilize it. Drive your hips up to lift the bar and unhook it from the machine. Thrust: Exhale and drive your hips up toward the ceiling until your body (from shoulders to knees) forms a straight line. Keep your chin tucked. Squeeze at the top: Pause at the top and squeeze your glutes hard. Lower with control: Inhale and lower your hips back down towards the floor, maintaining control. Repeat for the desired number of repetitions. Coach Tips: Your shins should be vertical at the top of the lift. If they are not, adjust your foot placement. Keep your chin tucked to your chest. This helps keep your spine neutral and focus on your glutes. The movement is a hinge from the hips, driven entirely by your glutes.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Smith Incline Bench Press',
    'SmithInclineBenchPress.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Smith Incline Bench Press Exercise for Chest</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Set the bench: Position an incline bench (set between 30-45 degrees) in the center of the Smith machine. Set the safety stoppers. Lie on the bench: Lie down so the bar is aligned directly over your upper chest (collarbone area). Plant your feet firmly on the floor. Grip the bar: Grasp the bar with an overhand grip, slightly wider than shoulder-width. Unrack: Rotate the bar to unhook it. Start with your arms fully extended. Lower the bar: Slowly lower the bar with control until it lightly touches your upper chest. Keep your elbows tucked slightly (not flared out). Press: Explosively press the bar straight back up to the starting position, squeezing your upper chest. Repeat: Repeat for the desired number of repetitions. When finished, re-rack the bar by rotating your wrists. Coach Tips: Keep your shoulder blades retracted and "screwed" into the bench to protect your shoulder joints. Do not let your glutes lift off the bench. Maintain your 3 points of contact (feet, glutes, upper back). The fixed path allows you to focus purely on contracting the upper pectoral muscles.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Standing Multi Hip Glute Kickback',
    'StandingMultiHipGluteKickback.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Standing Multi Hip Glute Kickback Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the machine: Adjust the rotating lever arm on the multi-hip machine so the pad is at a comfortable height. Select your weight. Position yourself: Stand facing the machine. Place the back of your working leg''s thigh (or Achilles, depending on machine design) against the roller pad. Brace: Grasp the support handles firmly. Keep your core tight and your standing (support) leg slightly bent. Kick back: Exhale and press your leg straight back, squeezing your glute hard at the peak of the contraction. Pause and squeeze: Hold the contraction for a second. Return with control: Inhale and slowly bring your leg back to the starting position, resisting the weight. Repeat: Complete all repetitions for one leg before switching to the other. Coach Tips: Keep your torso upright and stable. Avoid leaning forward or arching your lower back to get the weight back. The movement should be driven entirely by your glute. Focus on the "squeeze," not on how high you can kick. Keep the movement controlled, especially on the return.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Standing Multi Hip Thigh Abduction',
    'StandingMultiHipThighAbduction.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Standing Multi Hip Thigh Abduction Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the machine: Adjust the rotating lever arm on the multi-hip machine. Select your weight. Position yourself: Stand sideways to the machine. Place the outside of your working leg''s thigh against the roller pad. Brace: Grasp the support handles firmly. Keep your core tight and your standing leg slightly bent. Lift out: Exhale and push your leg straight out to the side, using your outer thigh and glute (gluteus medius). Pause and squeeze: Hold at the point of maximum contraction for a second. Return with control: Inhale and slowly bring your leg back to the starting position, resisting the weight. Repeat: Complete all repetitions for one leg before switching to the other. Coach Tips: Keep your torso perfectly upright. Do not lean to the side to "cheat" the weight up. Your standing leg and hips should remain stable and facing forward. Focus on pushing "out" with the side of your glute.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Standing Multi Hip Thigh Adduction',
    'StandingMultiHipThighAdduction.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Standing Multi Hip Thigh Adduction Exercise for Legs</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the machine: Adjust the rotating lever arm on the multi-hip machine. Select your weight. Position yourself: Stand facing the machine (or sideways, depending on setup). Place the inside of your working leg''s thigh against the roller pad. Brace: Grasp the support handles firmly. Keep your core tight and your standing leg slightly bent. Squeeze in: Exhale and sweep your working leg across the front of your body, squeezing your inner thigh (adductors). Pause and squeeze: Hold the contraction for a second at the end of the movement. Return with control: Inhale and slowly let your leg return to the starting position, resisting the weight. Repeat: Complete all repetitions for one leg before switching to the other. Coach Tips: Keep your torso stable and upright. Avoid twisting your hips or torso to swing the weight. The movement should be isolated to your inner thigh. Control the return phase; don''t just let the leg swing back.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Sumo Squat Jump Cardio',
    'SumoSquatJumpCardio.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Sumo Squat Jump Cardio Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Set your stance: Stand with your feet significantly wider than shoulder-width. Point your toes out at a 45-degree angle. Position your body: Keep your chest up, shoulders back, and core engaged. Squat down: Hinge at your hips and bend your knees, lowering your glutes down and back, as if sitting in a chair. Go as deep as you can while keeping your chest up. Explode up: From the bottom of the squat, explosively drive through your heels and jump vertically as high as you can. Land softly: Land softly on the balls of your feet first, then roll to your heels, immediately absorbing the impact by going into your next squat. Maintain form: Ensure your knees track in line with your toes (push them outwards). Repeat: Repeat the movement fluidly for the desired number of repetitions. Coach Tips: Focus on landing softly to protect your joints. The landing should be quiet. Keep your chest up and back straight throughout the entire movement. Do not let your chest collapse forward. Actively push your knees out during the squat and the landing to engage your glutes.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Vertical Leg Crunch',
    'VerticalLegCrunch.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Vertical Leg Crunch Exercise for ABS</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Lie on your back: Lie flat on your back and place your hands lightly behind your head for support, or by your sides. Lift your legs: Extend both legs straight up towards the ceiling. Keep them as straight as possible, with your feet together. Press back: Actively press your lower back into the floor. This is your starting position. Crunch up: Exhale and contract your abs to "crunch" your upper body, lifting your head and shoulder blades off the floor. Reach up: As you crunch, think about reaching your chest towards your shins (or the ceiling). Lower with control: Inhale and slowly lower your upper body back to the starting position, keeping your legs vertical. Repeat: Repeat the movement, keeping the tension in your abs. Coach Tips: Do not pull on your neck with your hands. Your hands are only there for light support; the work comes from your abs. Keep your legs as straight and vertical as possible. Do not let them swing for momentum. Focus on a "short" movement, lifting only your shoulder blades off the floor, to maximize abdominal contraction.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Bent Over Reverse Fly',
    'CableBentOverReverseFly.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Bent Over Reverse Fly Exercise for Shoulders</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm" target="_blank">Vector Fitness Exercises</a>',
    'Adjust the cables: Set both pulleys to the lowest (floor) position. Attach D-handles to each. Position yourself: Stand in the center of the machine. Grab the left handle with your right hand and the right handle with your left hand (so the cables are crossed). Hinge forward: Take a step back to create tension. Hinge at your hips, keeping your back straight, until your torso is nearly parallel to the floor. Starting position: Extend your arms down and in front of you with a slight, constant bend in your elbows. Pull (Fly): Exhale and, keeping your elbows slightly bent, pull your arms back and out to your sides in a wide "reverse fly" arc. Squeeze your back: Squeeze your shoulder blades together at the top of the movement. Focus on your rear deltoids and upper back. Return with control: Inhale and slowly reverse the motion, letting your arms cross in front of you again. Coach Tips: Your back must stay flat and straight. Do not round your spine. The bend in your elbows should remain constant. Do not "row" the weight; it''s a "fly" motion. Initiate the pull with your rear shoulders, not by pulling with your biceps or triceps.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Cable Lying Tricep Extension',
    'CableLyingTricepExtension.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Cable Lying Tricep Extension Exercise for Arm</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Adjust the cable: Set a pulley to the lowest (floor) position. Attach an EZ-curl bar or a straight bar. Position the bench: Place a flat bench in front of the machine, facing away from it. Position yourself: Lie flat on your back on the bench. Reach back with both hands and grab the bar with a close, overhand grip. Starting position: Pull the bar over your head so your arms are extended straight up over your chest, or angled slightly back towards your head. Lower the weight: Inhale and, keeping your upper arms stationary, bend only at your elbows, lowering the bar towards your forehead. Extend: Exhale and press the bar back up to the starting position by extending your elbows. Squeeze your tricep: Squeeze your triceps hard at the top of the movement. Repeat. Coach Tips: Keep your upper arms "pinned" in place. All movement should come from the elbow joint. Try to keep your elbows tucked in (pointing towards your knees), not flaring out to the sides. Control the negative (lowering) phase. This provides constant tension, which is a major benefit of using the cable.'
);

INSERT INTO exercises (name, media_file, attribution, description) VALUES (
    'Dumbbell Swing Cardio',
    'DumbbellSwingCardio.mp4',
    '<a href="https://iconscout.com/lottie-animations/woman" class="text-underline font-size-sm" target="_blank">Woman Doing Dumbbell Swing Cardio Exercise</a> by <a href="https://iconscout.com/contributors/lottie-di" class="text-underline font-size-sm">Vector Fitness Exercises</a> on <a href="https://iconscout.com" class="text-underline font-size-sm">IconScout</a>',
    'Select dumbbell: Grab a single dumbbell and hold it vertically with both hands, cupping one end (the "bell"). Set your stance: Stand with your feet slightly wider than shoulder-width apart, toes pointed slightly out. Hinge (The "Hike"): Keeping your back straight, "hike" the dumbbell back between your legs by pushing your hips backward. This is a hip-hinge, not a squat. Thrust (The "Swing"): Explosively drive your hips forward, squeezing your glutes hard. Propel the weight: Use the power from your hip thrust to propel the dumbbell up to chest or shoulder height. Your arms are just "guides" – they should not be lifting the weight. Return and repeat: Let the dumbbell swing back down under control, and immediately go into your next rep by hinging at the hips. Repeat: Repeat in a continuous, fluid, and explosive rhythm for the desired time. Coach Tips: This exercise is a hip-hinge, not a squat. Do not bend your knees excessively. The power comes 100% from your glutes and hips, not your arms. Keep your back flat (neutral spine) at all times. Do not round your lower back. Squeeze your glutes and abs hard at the top of the swing.'
);

-- Link exercises to body parts (many-to-many relationship)

INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (1, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (2, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (3, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (4, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (5, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (6, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (7, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (8, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (9, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (10, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (11, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (12, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (12, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (12, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (12, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (13, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (13, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (13, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (13, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (14, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (15, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (16, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (17, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (18, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (19, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (20, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (21, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (22, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (23, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (24, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (25, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (26, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (27, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (28, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (29, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (30, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (31, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (32, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (33, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (34, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (34, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (35, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (36, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (36, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (36, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (37, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (38, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (39, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (40, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (41, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (42, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (43, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (44, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (44, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (45, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (46, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (47, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (48, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (49, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (50, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (51, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (52, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (53, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (54, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (55, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (56, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (56, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (56, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (57, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (57, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (58, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (58, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (59, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (59, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (59, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (60, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (61, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (62, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (63, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (64, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (65, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (66, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (67, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (68, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (69, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (70, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (71, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (72, 3);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (73, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (74, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (75, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (76, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (77, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (78, 5);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (79, 4);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (80, 2);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (80, 1);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (80, 6);
INSERT INTO exercise_body_parts (exercise_id, body_part_id) VALUES (80, 5);


UPDATE exercises SET is_analyzable = TRUE WHERE name IN (
    'Assisted Parallel Grip Pull Up',
    'Barbell Back Squat',
    'Barbell Bench Press',
    'Barbell Bench Squat',
    'Barbell Bent Over Row',
    'Barbell Bulgarian Split Squat',
    'Barbell Glute Bridge',
    'Barbell Hip Thrust',
    'Barbell Incline Bench Press',
    'Barbell Preacher Bicep Curl',
    'Barbell Standing Shoulders Press',
    'Burpee Cardio',
    'Burpee No Jump Cardio',
    'Cable Bayesian Curl',
    'Cable Bench Fly',
    'Cable Bench Press',
    'Cable Bicep Curl',
    'Cable Close Grip Pulldown',
    'Cable Close Hammer Grip Pulldown',
    'Cable External Shoulder Rotation',
    'Cable Half Kneeling Face Pull',
    'Cable Half Kneeling Single Arm Row',
    'Cable High Pulley Rope Tricep Extension',
    'Cable Kneeling Crunch',
    'Cable Kneeling Donkey Kickback',
    'Cable Leaning Lateral Raise',
    'Cable One Arm Rope Tricep Pushdown',
    'Cable Shrug',
    'Cable Step Up',
    'Cable Upright Row',
    'Captains Chair Knee Raise',
    'Dead Bug',
    'Diagonal Plank',
    'Dumbbell Bench Fly',
    'Dumbbell Bench One Arm Tricep Kickback',
    'Dumbbell Bench Press',
    'Dumbbell Bicep Curl',
    'Dumbbell Bicep Curl Alternating',
    'Dumbbell Incline Bicep Curl',
    'Dumbbell Lying Tricep Extension',
    'Dumbbell Overhead One Arm Tricep Extension',
    'Dumbbell Overhead Weighted Sit Up',
    'Dumbbell Seated Lateral Raise',
    'High Knee Taps Cardio',
    'Lever Chest Press',
    'Lever Crunch',
    'Lever Lateral Raise',
    'Lever Leg Extension',
    'Lever Lying Leg Curl',
    'Lever Pec Deck',
    'Lever Pulldown',
    'Lever Seated Leg Curl',
    'Lever Standing Calf Raise',
    'Lying Leg Raise'
);
