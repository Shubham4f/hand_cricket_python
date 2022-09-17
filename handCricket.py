import random
import time
import cv2 as cv
import mediapipe as mp

mp_drawings = mp.solutions.drawing_utils
mp_drawings_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


class Player:
    def __init__(self, name):
        self.name = name
        self.isBatting = False
        self.score = 0

    def out(self):
        if self.isBatting:
            print(f"{self.name} got bold!!!")
        self.isBatting = not self.isBatting

    def add_score(self, round_score):
        print(f"{self.name} got {round_score} runs this round.")
        self.score += round_score
        print(f"{self.name}'s total runs till this round : {self.score}.")

    def innings2(self, target):
        run_required = target - self.score
        if run_required <= 0:
            return True
        else:
            print(f"{run_required} runs required to win.")
        return False


def get_runs(hand_landmark):
    landmarks = hand_landmark.landmark
    this_runs = 0
    for i in range(6, 20, 4):
        if landmarks[i].y > landmarks[i+2].y and landmarks[i-1].y > landmarks[i+2].y:
            this_runs += 1
    if this_runs == 0:
        if landmarks[20].y > landmarks[1].y and landmarks[3].y > landmarks[4].y:
            this_runs = 6
    return this_runs


def toss():
    while True:
        choice = input("Enter (H) for heads (T) for tails : ")
        choice = choice.lower()
        if choice == "h" or choice == "t":
            break
        print("Invalid Input try again!!!")
    result = random.choice(['Heads', 'Tails'])
    print("Flipping the coin...")
    time.sleep(3)
    print(f"It's {result}.")
    result = result[0].lower()
    time.sleep(3)
    if result == choice:
        while True:
            print(f"{p1.name} won the toss!!!\n"
                  "Enter following for your choice\n"
                  "1 for batting\n"
                  "2 for balling\n")
            innings_choice = int(input("Enter 1 or 2 :"))
            if innings_choice == 1 or innings_choice == 2:
                break
            print("Invalid Input try again!!!")
    else:
        print(f"{c1.name} won the toss!!!")
        innings_choice = random.choice([1, 2])
    if innings_choice == 1:
        p1.isBatting = True
        print(f"{p1.name} is batting first.")
    else:
        c1.isBatting = True
        print(f"{c1.name} is batting first.")


def game():
    pause = True
    out = False
    innings = 1
    target = 1
    p1_score = 0
    c1_score = 0

    vid = cv.VideoCapture(0)
    vid.set(3, 1280)
    vid.set(4, 720)

    timer = 0

    with mp_hands.Hands(model_complexity=0,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:
        while True:
            ret, frame = vid.read()
            if not ret or frame is None:
                break
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            result_frame = hands.process(frame)
            frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

            if result_frame.multi_hand_landmarks:
                for hand_landmarks in result_frame.multi_hand_landmarks:
                    mp_drawings.draw_landmarks(frame,
                                               hand_landmarks,
                                               mp_hands.HAND_CONNECTIONS,
                                               mp_drawings_styles.get_default_hand_landmarks_style(),
                                               mp_drawings_styles.get_default_hand_connections_style())

            frame = cv.flip(frame, 1)

            if timer == 50:
                h1 = 0
                h2 = 0
                c1_score = random.choice([1, 2, 3, 4, 6])
                if result_frame.multi_hand_landmarks and len(result_frame.multi_hand_landmarks) == 2:
                    h1 = get_runs(result_frame.multi_hand_landmarks[0])
                    h2 = get_runs(result_frame.multi_hand_landmarks[1])
                elif result_frame.multi_hand_landmarks and len(result_frame.multi_hand_landmarks) == 1:
                    h1 = get_runs(result_frame.multi_hand_landmarks[0])
                p1_score = h1 if h1 > h2 else h2
                print(f"{c1.name} : {c1_score}")
                print(f"{p1.name} : {p1_score}")
                if p1_score == c1_score:
                    target += c1.score if c1.isBatting else p1.score
                    c1.out()
                    p1.out()
                    out = True
                    if innings == 2:
                        break
                    print(f"{c1.name if c1.isBatting else p1.name} has to chase a target of {target} runs.")
                    innings += 1
                else:
                    c1.add_score(c1_score) if c1.isBatting else p1.add_score(p1_score)
                if innings == 2:
                    won = c1.innings2(target) if c1.isBatting else p1.innings2(target)
                    if won:
                        break
                    print("************************")
            if pause:
                timer = 0
                cv.putText(frame, f"Game Paused", (50, 50), cv.FONT_HERSHEY_COMPLEX, 1,
                           (0, 0, 255), 2, cv.LINE_AA)
            else:
                cv.putText(frame, f"Timer: {0 if timer > 50 else 50 - timer}", (50, 50), cv.FONT_HERSHEY_COMPLEX, 1,
                           (0, 0, 255), 2, cv.LINE_AA)
            cv.putText(frame, f"This round :-", (50, 100), cv.FONT_HERSHEY_COMPLEX, 1,
                       (0, 0, 255), 2, cv.LINE_AA)
            cv.putText(frame, f"{c1.name} : {c1_score}", (50, 130), cv.FONT_HERSHEY_COMPLEX, 1,
                       (255, 255, 0), 2, cv.LINE_AA)
            cv.putText(frame, f"{p1.name} : {p1_score}", (50, 160), cv.FONT_HERSHEY_COMPLEX, 1,
                       (255, 255, 0), 2, cv.LINE_AA)
            cv.putText(frame, f"Total Score :-", (50, 560), cv.FONT_HERSHEY_COMPLEX, 1,
                       (0, 0, 255), 2, cv.LINE_AA)
            cv.putText(frame, f"{c1.name} : {c1.score}", (50, 590),
                       cv.FONT_HERSHEY_COMPLEX, 1, (0, 252, 124) if c1.isBatting else (255, 255, 0), 2, cv.LINE_AA)
            cv.putText(frame, f"{p1.name} : {p1.score}", (50, 620),
                       cv.FONT_HERSHEY_COMPLEX, 1, (0, 252, 124) if p1.isBatting else (255, 255, 0), 2, cv.LINE_AA)
            cv.putText(frame, f"{c1.name if c1.isBatting else p1.name} has the bat.", (50, 670),
                       cv.FONT_HERSHEY_COMPLEX, 1, (0, 252, 124), 2, cv.LINE_AA)
            if innings == 2:
                cv.putText(frame, f"Target Remaining : {target - (c1.score if c1.isBatting else p1.score)}", (50, 350),
                           cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
            timer = (timer + 1) % 100
            if out:
                cv.putText(frame, f"OUT!!!", (560, 350),
                           cv.FONT_HERSHEY_COMPLEX, 3, (0, 0, 255), 2, cv.LINE_AA)
                pause = True
                timer = (timer + 1) % 100

            cv.imshow('Hand Cricket', frame)
            if cv.waitKey(1) & 0xFF == ord("p"):
                pause = not pause
                out = False
                timer = 0

    vid.release()
    cv.destroyAllWindows()

    print("************************")
    print(f"{c1.name}'s total runs : {c1.score}")
    print(f"{p1.name}'s total runs : {p1.score}")
    if c1.score == p1.score:
        print("Match tie\n"*5)
    else:
        win = c1 if c1.score > p1.score else p1
        print(f"{win.name} won the match!!!\n"*5)
        del win


c1 = Player("Computer")
user_name = input("Enter Your Name : ")
p1 = Player(user_name)
while True:
    toss()
    game()
    c1.score = 0
    p1.score = 0
    c1.isBatting = False
    p1.isBatting = False
    again = input("To play again enter P :")
    again = again.lower()
    if again == 'p':
        print("Starting a new match!!!")
    else:
        print("Thanks for playing!!!")
        break
