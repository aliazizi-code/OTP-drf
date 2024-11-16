from rest_framework.throttling import UserRateThrottle


class MinuteThrottle(UserRateThrottle):
    rate = '2/minute'


class DayThrottle(UserRateThrottle):
    rate = '10/day'
