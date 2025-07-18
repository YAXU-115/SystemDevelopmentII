class CsvClass:

    def __init__(self,filename):
        self.filename = filename

    def read_csv(self):
        with open(self.filename,"r",encoding="UTF-8") as file:
            read_files = file.readlines()
            return read_files
    
    def append_csv(self,message):
        with open(self.filename,"a",encoding="UTF-8") as file:
            file.write(message)
    
    def change_csv(self, client_name, temperature, humidity, pressure, altitude, fan_duty, time):
        message = f"{client_name},{temperature},{humidity},{pressure},{altitude},{fan_duty},{time}" + "\n"
        return message


