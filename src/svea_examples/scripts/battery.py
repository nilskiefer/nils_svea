#! /usr/bin/env python3

import rospy
from std_msgs.msg import Header
from svea_msgs.msg import energy_sensor, Battery as BatteryCombined

class BatteryNode:
    def __init__(self):
        rospy.init_node('rudamentary_battery_node')
        self.battery = None
        self.charger = None

        self.pub = rospy.Publisher('/battery/', BatteryCombined, queue_size=10)
        rospy.Subscriber('/energy_sensors/battery', energy_sensor, self.sensor_cb, callback_args='battery')
        rospy.Subscriber('/energy_sensors/charger', energy_sensor, self.sensor_cb, callback_args='charger')

    def sensor_cb(self, msg, sensor_type):
        if sensor_type == 'battery':
            self.battery = msg
        elif sensor_type == 'charger':
            self.charger = msg

    def spin(self):
        if self.battery is None or self.charger is None:
            return

        combined = BatteryCombined()
        combined.header = Header(stamp=rospy.Time.now())
        combined.battery = self.battery
        combined.charger = self.charger
        # Use the battery's percentage if available; otherwise default to 0.
        combined.percentage = 0.0
        # Compute net_energy as the difference between battery and charger power.
        combined.net_energy = self.battery.power - self.charger.power
        self.pub.publish(combined)

    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            self.spin()
            rate.sleep()

if __name__ == '__main__':
    BatteryNode().run()