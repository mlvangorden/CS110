
import sqlite3

class PopDB:
    def __init__(self, dbname):
        self.population = 0
        self.city = ""
        connect = sqlite3.connect(dbname)
        self.cursor = connect.cursor()
        
    def setCity(self, name):
        self.city = name
        
    def getPopulation(self):
        self.cursor.execute("SELECT population FROM city WHERE name = ? ", self.city)
        
    def getNumCities(self):
        self.cursor.execute("SELECT Count(population) FROM city")
        
        
    def __str__(self):
        value = self.cursor.fetchone()
        if value:
            return "The population of " + value[0] + " is " + value[1] + "."
        else:
            return "City not found."

def main():
    query = PopDB("WorldPopulation.db")
    city = input("Enter the name of a city (use _ instead of spaces): ")


    while(city):
        if(query.setCity(city) != None):
            query.getPopulation()
            print(query)
           
           
        else:
            print("Invalid city name")
            
        city = input("Enter the name of a city (use _ instead of spaces). Enter to close")
        
    
main()