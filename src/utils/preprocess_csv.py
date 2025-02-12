def preprocess_csv(file_path, output_path, num_columns):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_path, 'w', encoding='utf-8') as f:
        for line in lines:
            columns = line.strip().split(',')
            if len(columns) < num_columns:
                columns.extend([''] * (num_columns - len(columns)))
            f.write(','.join(columns) + '\n')