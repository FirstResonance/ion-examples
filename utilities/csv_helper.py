import csv


class CsvHelper:
    def write_to_csv(items_list, csv_file_path):
        with open(csv_file_path, "w") as f:
            writer = csv.writer(f)
            columns = items_list[0].keys()
            writer.writerow(columns)
            for row in items_list:
                row_data = []
                for column in columns:
                    row_data.append(row.get(column))
                writer.writerow(row_data)

    def read_from_csv(csv_file_path):
        csv_data = []
        with open(csv_file_path, newline="") as f:
            reader = csv.reader(f, delimiter=",", quotechar='"')
            for row in reader:
                csv_data.append(row)
        return csv_data
