import pigo
import time  # import just in case students need
import random

# setup logs
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/PnR-Final/log_robot.log"  # don't forget to make this file!
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)


class Piggy(pigo.Pigo):
    """Student project, inherits teacher Pigo class which wraps all RPi specific functions"""

    def __init__(self):
        """The robot's constructor: sets variables and runs menu loop"""
        print("I have been instantiated!")
        # Our servo turns the sensor. What angle of the servo( ) method sets it straight?
        self.MIDPOINT = 75
        # YOU DECIDE: How close can an object get (cm) before we have to stop?
        self.SAFE_STOP_DIST = 50
        self.HARD_STOP_DIST = 45
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.LEFT_SPEED = 130
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.RIGHT_SPEED = 135
        # This one isn't capitalized because it changes during runtime, the others don't
        self.turn_track = 0
        # Our scan list! The index will be the degree and it will store distance
        self.scan = [None] * 180
        self.turn_count=0
        self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
        # let's use an event-driven model, make a handler of sorts to listen for "events"
        if __name__ == "__main__":
            while True:
                self.stop()
                self.menu()


    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values
        # You may change the menu if you'd like to add an experimental method
        menu = {"n": ("Navigate forward", self.nav),
                "d": ("Dance", self.dance),
                "o": ("Obstacle count", self.obstacle_count),
                "c": ("Calibrate", self.calibrate),
                "t": ("Test", self.skill_test),
                "s": ("Check status", self.status),
                "h": ("Open House", self.open_house),
                "q": ("Quit", quit_now)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = raw_input("Your selection: ")
        # activate the item selected
        menu.get(ans, [None, error])[1]()

    def skill_test(self):
        '''demonstrates two nav skills'''
        choice = raw_input("Left/Right or Turn Until Clear?")
        if "l" in choice: #picks left or right
            self.wide_scan(count=4) #scan the area
            # create two variables, left_total and right_total
            left_total = 0
            right_total = 0
            # loop from self.MIDPOINT - 60 to self.MIDPOINT
            for angle in range(self.MIDPOINT - 60, self.MIDPOINT):
                if self.scan[angle]:
                    # add up the numbers to right_total
                    right_total += self.scan[angle]
            # loop from self.MIDPOINT to self.MIDPOINT + 60
            for angle in range(self.MIDPOINT, self.MIDPOINT + 60):
                if self.scan[angle]:
                    # add up the numbers to left_total
                    left_total += self.scan[angle]
            # if right is bigger:
            if right_total > left_total:
                # turn right
                self.encR(4)
            # if left is bigger:
            if left_total > right_total:
                # turn left
                self.encL(4)


        else:
            print("I'll keep turning until it's clear")
            #while it's not clear
            while not self.is_clear():
                self.encR(1)


    def open_house(self):
        """reacts to dist measurement in a cute way"""
        while True:
            if self.dist() < 30:
                self.escape()
            time.sleep(.1)

    def escape(self):
        self.encB(5)
        self.encR(5)
        self.bob_head()

    # YOU DECIDE: How does your GoPiggy dance?
    def dance(self):
        if not self.safe_to_dance():
            print("\n---- NOT SAFE TO DANCE ----\n")
        if self.safe_to_dance():
            print("\n----LET'S DANCE----\n")
            self.shake_body()
            self.dancing_forward()
            self.bob_head()
            self.go_discontinuously()
            self.turn_back()
            self.bob_head()
            self.shake_body()
            self.go_discontinuously()
            self.bob_head()
            self.dancing_forward()
            self.turn_back()
            self.bob_head()
        '''self.encF(18)
        self.encB(10)
        self.encR(36)
        self.encF(7)
        self.encB(5)
        self.encL(36)
        self.encR(5)
        self.encL(5)
        self.encB(18)
        self.wide_scan()
        self.encR(18)
        self.encF(10)
        self.encL(18)'''

    def safe_to_dance(self):
        for x in range(8):
            if not self.is_clear():
                return False
            self.encR(3)
        return True

    def dancing_forward(self):
        for x in range(3):
            self.servo(self.MIDPOINT - 30)
            self.encR(2)
            self.servo(self.MIDPOINT)
            self.encF(5)
            self.servo(self.MIDPOINT + 30)
            self.encL(2)
            self.servo(self.MIDPOINT)
            self.encF(5)

    #From Mr.A
    def bob_head(self):
        for y in range(3):
            for x in range(self.MIDPOINT - 30, self.MIDPOINT +30, 15):
                self.servo(x)
        self.servo(self.MIDPOINT)

    def shake_body(self):
        for x in range(2):
            self.servo(self.MIDPOINT - 30)
            self.encL(26)
            self.servo(self.MIDPOINT + 30)
            self.encR(26)
            self.servo(self.MIDPOINT)
            self.encF(3)
            self.servo(self.MIDPOINT - 30)
            self.encL(18)
            self.servo(self.MIDPOINT + 30)
            self.encR(18)
            self.servo(self.MIDPOINT)
            self.encB(3)
        time.sleep(1)


    def turn_back(self):
        for x in range(2):
            self.encB(10)
            self.encR(3)
            self.encB(10)
            self.encL(3)

    def go_discontinuously(self):
        for x in range(3):
            self.encF(3)
        for y in range(2):
            for x in range(3):
                self.encL(1)
            for x in range(6):
                self.encR(1)
            for x in range(3):
                self.encL(1)
        for x in range(3):
            self.encB(5)
            self.encF(2)


    def obstacle_count(self):
        """scans and estimates the number of obstacles within sight"""
        self.wide_scan()
        found_something = False
        counter = 0
        for x in range(4):
            for ang, distance in enumerate(self.scan):
                if distance and distance < 200 and not found_something:
                    found_something = True
                    counter += 1
                    print("Object # %d found, I think" % counter)
                if distance and distance > 200 and found_something:
                    found_something = False
        print("\n----I SEE %d OBJECTS----\n" % counter)

    def safety_check(self):
        """subroutine of the dance method"""
        self.servo(self.MIDPOINT)  # look straight ahead
        for loop in range(4):
            if not self.is_clear():
                print("NOT GOING TO DANCE")
                return False
            print("Check #%d" % (loop + 1))
            self.encR(8)  # figure out 90 deg
        print("Safe to dance!")
        return True

    def is_clear_infront(self):
        """ checks the scan array to see if there's a path dead ahead """
        # check for obstacles
        for angle in range(self.MIDPOINT - 5, self.MIDPOINT +5):
            if self.scan[angle] and self.scan[angle] < self.SAFE_STOP_DIST:
                '''if the distance between mid-5 and mid+5 is bigger than the safe stop distance, 
                go straight rather than turning left or right'''
                return False


    def direction_choice(self):
        # the method to choose direction that where has the longest distance to go
        self.wide_scan(count=5)
        # scan the area
        # create 4 variables, use to compare the value later
        m = {'left1_total': 0, 'left2_total': 0, 'right1_total': 0, 'right2_total': 0}
        # loop from self.MIDPOINT - 60 to self.MIDPOINT - 30
        for angle in range(self.MIDPOINT - 60, self.MIDPOINT - 30):
            if self.scan[angle]:
                # add up the numbers to right1_total
                m['right1_total'] += self.scan[angle]
                # this is used to compare the distance later
        # loop from self.MIDPOINT - 30 to self.MIDPOINT
        for angle in range(self.MIDPOINT - 30, self.MIDPOINT):
            if self.scan[angle]:
                # add up the numbers to right2_total
                m['right2_total'] += self.scan[angle]
                # this is used to compare the distance later
        # loop from self.MIDPOINT to self.MIDPOINT + 30
        for angle in range(self.MIDPOINT, self.MIDPOINT + 30):
            if self.scan[angle]:
                # add up the numbers to left2_total
                m['left2_total'] += self.scan[angle]
                # this is used to compare the distance later
        # loop from self.MIDPOINT + 30 to self.MIDPOINT + 60
        for angle in range(self.MIDPOINT + 30, self.MIDPOINT + 60):
            if self.scan[angle]:
                # add up the numbers to left1_total
                m['left1_total'] += self.scan[angle] # this is used to compare the distance later

        '''if m['left1_total'] + m['right1_total'] + m['right2_total'] + m['left2_total'] < 600:
            self.encL(6)'''
        # check if no turn is necessary, perhaps choose_direction was activated by error
        if self.is_clear_infront():
            self.cruise()
        # if left1 is bigger:
        elif max(m, key=m.get) == 'left1_total':
            self.encL(3)
            # turn left 3 units
            self.turn_count += 2
            # when robot turn 3 units left, add 2 to the error count
        # if left2 is bigger:
        elif max(m, key=m.get) == 'left2_total':
            self.encL(2)
            # turn left 2 units
            self.turn_count += 1
            # when robot turn 2 units left, add 1 to the error count
        # if right1 is bigger:
        elif max(m, key=m.get) == 'right1_total':
            self.encR(3)
            # turn right 3 units
            self.turn_count -= 2
            # when robot turn 3 units right, minus 2 to the error count
        # if right2 is bigger:
        elif max(m, key=m.get) == 'right2_total':
            self.encR(2)
            # turn right 2 units
            self.turn_count -= 1
            # when robot turn 2 units right, minus 1 to the error count


    def nav(self):
        """auto pilots and attempts to maintain original heading"""
        logging.debug("Starting the nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------  [ Press CTRL + C to stop me ]  -------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")

        error_count = 0
        while True:
            # Check if it is clear over and over again.
            print("TOP OF NAV LOOP")
            # sign to start while true loop
            if self.is_clear():
                # the method to check if it is clear
                self.cruise()
                # if the area is clear, start self.cruise method
            else:
                # if it is not clear, go back and find a path between right and left.
                if self.turn_count > 7:
                    '''if the error count is too big, 
                    the robot might go to the opposite direction, 
                    which need to turn another way'''
                    raw_input("Hey, what's up?")
                    # check if the robot need to fix its way
                    self.encB(3)
                    self.encR(10)
                    self.turn_count -= 7
                    # make the error count back to zero
                elif self.turn_count < -7:
                    '''if the error count is too small, 
                    the robot might go to the opposite direction, 
                    which need to turn another way'''
                    raw_input("Hey, what's up?")
                    # check if the robot need to fix its way
                    self.encB(3)
                    self.encL(10)
                    self.turn_count += 7
                    # make the error count back to zero
                else:
                    self.encB(2)
                    self.direction_choice()




    def cruise(self):
        """ drive straight while path is clear """
        print("GO FORWARD!!!") # signal that robot is running this method
        self.fwd() # robot keeps going forward
        while self.is_clear(count=30, step=30):
            # scan the area from midpoint-30 to midpoint+30, each time +15 degree
            pass
            # if it is clear, do nothing.
        print("CRUISE WHILE LOOP STOPPED")
        self.stop()
        # if the area is not clear, stop, and go back to self.nav method
####################################################
############### STATIC FUNCTIONS

def error():
    """records general, less specific error"""
    logging.error("ERROR")
    print('ERROR')


def quit_now():
    """shuts down app"""
    raise SystemExit

##################################################################
######## The app starts right here when we instantiate our GoPiggy


try:
    g = Piggy()
except (KeyboardInterrupt, SystemExit):
    pigo.stop_now()
except Exception as ee:
    logging.error(ee.__str__())
