import discord, os, json, requests, datetime, pytz, asyncio
from keepAlive import keep_alive

# weather app specific configs
APPID = os.environ['APPID']
lat = os.environ['lat']
lon = os.environ['lon']
tz = pytz.timezone(os.environ['TZ'])


def getWeather(message):
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=alerts&appid={APPID}'
    response = requests.get(url)
    response.raise_for_status()
    apiResponse = json.loads(response.text)
    # app 
    d = apiResponse['daily']
    # m = apiResponse['minutely']
    # h = apiResponse['hourly']
    c = apiResponse['current']

    precipToday = d[0]['pop']
    currTemp = round(float(c['temp']-273.15),1)
    currHumidity = round(c['humidity'])
    currDescr = (f"{c['weather'][0]['main']} - {c['weather'][0]['description']}")
    currClouds = round(c['clouds'])
    currWind = round(c['wind_speed'],1)
    currUV = round(c['uvi'],1)
    sunrise0 = datetime.datetime.fromtimestamp(c['sunrise'], tz).strftime('%H:%M')
    sunset0 = datetime.datetime.fromtimestamp(c['sunset'], tz).strftime('%H:%M')
    timedelta0 = datetime.timedelta(seconds=c['sunset']-c['sunrise'])
    dayLength0 = ':'.join(str(timedelta0).split(':')[:2])
    humidity0 = round(d[0]['humidity'])
    descr0 = (f"{d[0]['weather'][0]['main']} - {d[0]['weather'][0]['description']}")
    minTemp0 = round(float(d[0]['temp']['min']-273.15),1)
    maxTemp0 = round(float(d[0]['temp']['max']-273.15),1)
    windSpeed0 = round(d[0]['wind_speed'])
    clouds0 = round(d[0]['clouds'])
    rainfall0 = round(d[0]['rain'])
    uvi0 = round(d[0]['uvi'],1)

    if message == 'umbrellaMessage':
        #umbrellaMessage"
        if precipToday == 0:
            umbrellaMessage = (f'Sunshine and rainbows, my friend! - {str(round(precipToday*100))}% rain')
        elif precipToday > 0 and precipToday <= 0.25:
            umbrellaMessage = (f"I wouldn't worry about it - {str(round(precipToday*100))}% rain")
        elif precipToday > 0.25 and precipToday <= 0.5:
            umbrellaMessage = (f"Maybe some sprinkles here and there, take an umbie if you're feeling scared - {str(round(precipToday*100))}% rain")
        elif precipToday > 0.5 and precipToday <= 0.75:
            umbrellaMessage = (f'You gonna get wet more likely than not - {str(round(precipToday*100))}% rain')
        elif precipToday > 0.75 and precipToday < 1:
            umbrellaMessage = (f"IT'S GONNA RAIN! - {str(round(precipToday*100))}% rain")
        elif precipToday == 1:
            umbrellaMessage = (f"IT'S BAD! - {str(round(precipToday*100))}% rain")
        return umbrellaMessage

    elif message == 'rightNow':
        #rightNow
        rightNow = (f'Current weather:\nTemp: {currTemp}°C, Humidity: {currHumidity}%\nClouds: {currClouds}%, Wind: {currWind}m/s\nUV index: {currUV}\n{currDescr}')
        return rightNow

    elif message == 'today':
        #todayForecast
        todayForecast = (f'''Today's weather forecast:\nSunrise: {sunrise0}, Sunset: {sunset0}, Day length: {dayLength0}\nMin temp: {minTemp0}°C, Max temp: {maxTemp0}°C\nMax rain chance: {str(round(precipToday*100))}%, Clouds: {clouds0}%\nRainfall: {rainfall0}mm, UV Index: {uvi0}\nHumidity: {humidity0}%, Wind speed: {windSpeed0}m/s\nSummary: {descr0}''')
        return todayForecast

    elif message == 'blaccuweather':
        #blaccuweather GIF
        if precipToday > 0.5 and windSpeed0 > 10:
            ollieGif = (f'https://c.tenor.com/BqQ6TQaM8m0AAAAC/donuts-rain.gif')
        elif precipToday > 0.5:
            ollieGif = (f'https://c.tenor.com/KcqtH2ff4kIAAAAC/weather-rain.gif')
        elif precipToday < 10 and windSpeed0 < 8 and maxTemp0 < 27 and clouds0 < 50:
            ollieGif = (f'https://c.tenor.com/ABk_OPaxWd0AAAAC/ollie-williams.gif')
        return ollieGif

# discord bot config
client=discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await daily_weather()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
      
# Hit me -> Today's precip  
    if 'hit me' in message.content.lower():
        await message.channel.send(getWeather('umbrellaMessage'))

# Right now -> Current status  
    if 'right now' in message.content.lower():
        await message.channel.send(getWeather('rightNow'))
  
# Today -> Today's forecast  
    if 'today' in message.content.lower():
        await message.channel.send(getWeather('today'))

# Blaccuweather -> GIF
    if 'blaccuweather' in message.content.lower():
        await message.channel.send(getWeather('blaccuweather'))

# Daily forecast at 8:00
async def daily_weather():
    now = datetime.datetime.now(tz)
    then = now + datetime.timedelta(days=1)
    then.replace(hour=8, minute=0)
    wait_time = (then-now).total_seconds()
    await asyncio.sleep(wait_time)
    channel = client.get_channel(int(os.environ['CHANNEL']))
    await channel.send(getWeather('today'))
    await channel.send(getWeather('blaccuweather'))

keep_alive()
client.run(os.environ['TOKEN'])