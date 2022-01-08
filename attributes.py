import math, random

versionNumber = 1

#Class and function definitions
class Attribute:
    """Contains a name string and a value float."""
    def __init__(self, name:str, value:float):
        self.name = name
        self.value = value

    def newValue(self, new):
        self.value = new

    def twitterFormat(self):
        frac, whole = math.modf(self.value/20)
        valueString = ""
        valueString += "🟩"*int(whole) #green square
        if frac > 0.1 and frac < 0.5:
            valueString += "🟧" #orange square
        elif frac >= 0.5 and frac < 0.9:
            valueString += "🟨" #yellow square
        elif frac > 0.9:
            valueString += "🟩" #green square
        while len(valueString) < 5:
            valueString += "🟥" #red square
        return f"{valueString} - {self.name}"

    def __str__(self):
        return f"{self.name}: {int(self.value)}"

    #Comparison helpers
    def __eq__(self, other): #can compare attributes by name, or find attribute by value
        if isinstance(other, Attribute):
            return self.name == other.name
        elif isinstance(other, int):
            return self.value == other
        else:
            return False

    def __ne__(self, other):
        return not self == other

    #less than/greater than compare attributes by value, or compare value to int
    def __lt__(self, value):
        if isinstance(other, Attribute):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        else:
            return False

    def __le__(self, value):
        if isinstance(other, Attribute):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other
        else:
            return False

    def __gt__(self, other):
        if isinstance(other, Attribute):
            return self.value > other.value
        elif isinstance(other, int):
            return self.value > other
        else:
            return False

    def __ge__(self, other):
        if isinstance(other, Attribute):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other
        else:
            return False
        
        

def normalDis(generator:random.Random, mean:float, stdDev:float, min:float=-math.inf, max:float=math.inf) -> float:
    """Generates random number from normal distribution with given mean and standard deviation. Optionally takes min and max values."""
    num = generator.gauss(mean, stdDev)
    while min > num or num > max:
        num = generator.gauss(mean, stdDev)
    return num

#Attributes to generate
#["sample name", mean, stdDev, min(optional), max(optional)]
masterList = [
    ["Speed", 60, 25, 0, 100], #sprint speed (Forward)
    ["Agility", 50, 35, 0, 100], #changing directions/goaltending slide (Goalie)
    ["Reflexes", 50, 35, 0, 100], #deflections/goaltending blocks/intercepting passes (Goalie)
    ["Strength", 40, 60, 0, 100], #power of slapshot/body checking (Defense)
    ["Dexterity", 50, 25, 10, 100], #power of wrist shot/dekes (Forward)
    ["Shot Accuracy", 40, 25, 10, 100], #accuracy on shots (Secondary/All Skaters)
    ["Pass Accuracy", 60, 35, 0, 100], #does what you think it does (Defense)
    ["Wisdom", 40, 50, 0, 100], #takes better shots/makes safer passes (Secondary/All)
    ["Stickhandling", 50, 35, 0, 100], #dekes/checking (Secondary/All)
    ["Discipline", 75, 60, 0, 100], #Higher means less penalties
    ["Intelligence", 50, 50, 0, 100], #Skill at positioning (as skater or goalie) (Secondary/All)
    ["Constitution", 60, 20, 0, 100] #Stamina/injury resilience
    ]

noPrint = [
    "Discipline",
    "Constitution"
    ]
    
def attributesFromName(name:str):
    """Returns a List of Attribute objects, seeded by the name parameter."""
    generator = random.Random() #individual random instance to avoid conflicts
    generator.seed(name)
    atrs = [versionNumber] #in case of stat changes, record which number to use
    for template in masterList:
        atrs.append(Attribute(template[0], normalDis(generator, *template[1:])))
    return atrs