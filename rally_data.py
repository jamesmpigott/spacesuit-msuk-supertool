import requests
import os
import csv
import tkinter as tk
from tkinter import messagebox


class RallyData:
    def __init__(self, input_url):
        self.input_url = input_url
        self.base = os.path.dirname(input_url)
        self.columns_to_keep = [
            {
                "nicename": "No",
                "name": "no"
            },
            {
                "nicename": "Driver",
                "name": "pe_name_d"
            },
            {
                "nicename": "Champs",
                "name": "champ_d"
            },
            {
                "nicename": "Co-Driver",
                "name": "pe_name_n"
            },
            {
                "nicename": "Car",
                "name": "ca_make"
            }
        ]
        self.data = None
        self.transformed_data = None
        self.headers = [column["nicename"] for column in self.columns_to_keep]
    
    def fetch_data(self):
        """Fetch rally entry data from the server"""
        try:
            self.data = requests.get(f"{self.base}/entries_get.php?type=s&combined=0&mixed=0").json()
            return self.data
        except:
            messagebox.showerror("Invalid URL.", f"{self.input_url} is not a valid url.")
            return
            
    
    def transform_data(self):
        """Transform the data according to column specifications"""
        if self.data is None:
            self.fetch_data()
            
        self.transformed_data = []
        for item in self.data:
            item_data = {}
            for column in self.columns_to_keep:
                if column["name"] == "ca_make":
                    # Merge make and model into a single "Car" field
                    item_data[column["nicename"]] = f"{item['ca_make']} {item['ca_model']}"
                else:
                    item_data[column["nicename"]] = item[column["name"]]
            self.transformed_data.append(item_data)
            
        return self.transformed_data
    
    def export_to_csv(self, output_directory, filename="rally_entries.csv"):
        """Export the transformed data to a CSV file"""
        if self.transformed_data is None:
            self.transform_data()
        path = output_directory + '/' + filename
        with open(path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.transformed_data)
            
        print(f"Data exported to {path}")

        response = messagebox.askquestion(
            "Complete",
            type='yesno',
            icon='info',
            detail='Would you like to open the output folder?'
        )
        if response == 'yes':
            os.system(f'open "{output_directory}"')

        return path
    
    def get_transformed_data(self):
        """Get the transformed data"""
        if self.transformed_data is None:
            self.transform_data()
        return self.transformed_data
    
    
    