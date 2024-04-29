class IncreaseSpeed:
    def __init__(self, current_speed, max_speed):
        self.current_speed = current_speed
        self.max_speed = max_speed

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_speed < self.max_speed:
            self.current_speed += 10
            if self.current_speed > self.max_speed:
                self.current_speed = self.max_speed
            return self.current_speed
        else:
            raise StopIteration


class DecreaseSpeed:
    def __init__(self, current_speed):
        self.current_speed = current_speed

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_speed > 0:
            self.current_speed -= 10
            if self.current_speed < 0:
                self.current_speed = 0
            return self.current_speed
        else:
            raise StopIteration


class Car:
    cars = 0
    on_road = True

    def __init__(self, max_speed: int, current_speed=0):
        Car.cars += 1
        self.max_speed = max_speed
        self.current_speed = current_speed

    def accelerate(self, border=None):
        speed = self.current_speed
        if not Car.on_road:
            print("Car is currently parked. Cannot accelerate.")
            return

        gaz = IncreaseSpeed(self.current_speed, self.max_speed)
        if border is not None and self.current_speed < border:
            for speed in gaz:
                print("Current speed:", speed)
                self.current_speed = speed
                if speed == border:
                    self.current_speed = border
                    break
        elif border is None and self.current_speed < self.max_speed:
            speed = next(gaz)
            print("Current speed:", speed)
            self.current_speed = speed

    def brake(self, border=None):
        speed = self.current_speed
        if not Car.on_road:
            print("Car is currently parked. Cannot brake.")
            return

        tormoz = DecreaseSpeed(self.current_speed)
        if border is not None and self.current_speed > border:
            for speed in tormoz:
                print("Current speed:", speed)
                self.current_speed = speed
                if speed == border:
                    self.current_speed = speed
                    break
        elif border is None and self.current_speed > 0:
            speed = next(tormoz)
            print("Current speed:", speed)
            self.current_speed = speed
    @classmethod
    def parking(cls, car):
        if  car.on_road:
            car.on_road = False
            cls.cars -= 1
            print("Car is now off the road.")
        else:
            print("Car is already off the road or not found.")

    @staticmethod
    def total_cars():
        print("Total number of cars on the road:", Car.cars)



    def show_weather():
        import openmeteo_requests
        import datetime
        openmeteo = openmeteo_requests.Client()
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
          "latitude": 59.9386, # for St.Petersburg
          "longitude": 30.3141, # for St.Petersburg
          "current": ["temperature_2m", "apparent_temperature", "rain", "wind_speed_10m"],
          "wind_speed_unit": "ms",
          "timezone": "Europe/Moscow"
          }
        response = openmeteo.weather_api(url, params=params)[0]

        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_apparent_temperature = current.Variables(1).Value()
        current_rain = current.Variables(2).Value()
        current_wind_speed_10m = current.Variables(3).Value()

        return print(f"Current time: {datetime.datetime.fromtimestamp(current.Time()-response.UtcOffsetSeconds())} {response.TimezoneAbbreviation().decode()}\n"
                      f"Current temperature: {round(current_temperature_2m, 0)} C\n"
                      f"Current apparent_temperature: {round(current_apparent_temperature, 0)} C\n"
                      f"Current rain: {current_rain} mm\n"
                      f"Current wind_speed: {round(current_wind_speed_10m, 1)} m/s")



# oka = Car(max_speed=120, current_speed=50)
# oka.accelerate(100)
# oka.brake(30)

# uaz = Car(max_speed=150)
# uaz.accelerate()
# uaz.accelerate(160)
# uaz.brake()

# Car.show_weather()

# oka = Car(1,1)
# uaz = Car(1,1)
# niva = Car(1,1)


# Car.total_cars()


# Car.parking(oka)
# Car.parking(uaz)


# Car.total_cars()


