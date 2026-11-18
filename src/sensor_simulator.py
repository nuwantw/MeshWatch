
import random


def generate_reading():
    """Generate simulated environmental sensor readings."""
    return {
        "temperature": round(random.uniform(15, 35), 2),
        "humidity": round(random.uniform(30, 80), 2),
        "light": round(random.uniform(0, 1000), 2),
    }


def main():
    reading = generate_reading()

    print(f"Temperature: {reading['temperature']} °C")
    print(f"Humidity: {reading['humidity']} %")
    print(f"Light: {reading['light']} lux")


if __name__ == "__main__":
    main()
