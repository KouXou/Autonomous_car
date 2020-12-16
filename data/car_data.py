from pandas import DataFrame
import datetime


class CarData:
    def __init__(self):
        self.columns = ['Move', 'Created_On', 'Direction', 'Speed']

    def create_df(self):
        driver = {}
        df = DataFrame(driver, columns=self.columns)
        return df

    def addToDataFrame(self, df, direction, move, speed):
        return df.append({'Move': move,
                          'Created_On': datetime.datetime.now(),
                          'Direction': direction,
                          'Speed': speed}, ignore_index=True)


class CsvFile:

    def __init__(self, csv_name):
        super().__init__()
        self.csv_name = csv_name

    def printDataFrame(self, df):
        print(df)

    def export_file(self, df, path):
        #    filename = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
        ##   export_csv = df.to_csv (r'./' + filename + '.csv', index = True, index_label= 'Index', header=True)
        #    df.to_csv (r'./' + filename + '.csv', index = False, header=True)
        df.to_csv(path + self.csv_name, index=False, header=True)
