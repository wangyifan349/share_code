import os
import sqlite3

def get_all_files(directory, extensions):
    """Get all files with specified extensions in the directory and its subdirectories."""
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                file_list.append(os.path.join(root, file))
    return file_list

def insert_into_db(db_name, data):
    """Insert data into the SQLite database, avoiding duplicates."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            UNIQUE(title, content)
        )
    ''')
    for item in data:
        try:
            cursor.execute('INSERT INTO files (title, content) VALUES (?, ?)', item)
        except sqlite3.IntegrityError:
            continue
    conn.commit()
    conn.close()

def query_db(db_name, keyword):
    """
    Query the database for records matching the keyword in title or content,
    and sort the results in descending order:
    - First, records where the keyword appears in the title.
    - Then, records where the keyword appears in the content, ordered by the number of occurrences.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    keyword_like = f'%{keyword}%'
    keyword_length = len(keyword) if len(keyword) > 0 else 1  # Avoid division by zero
    cursor.execute('''
        SELECT 
            id,
            title, 
            content,
            CASE WHEN title LIKE ? THEN 1 ELSE 0 END AS in_title,
            (LENGTH(content) - LENGTH(REPLACE(content, ?, ''))) / ? AS occurrences
        FROM files
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY in_title DESC, occurrences DESC
    ''', (keyword_like, keyword, keyword_length, keyword_like, keyword_like))
    results = cursor.fetchall()
    conn.close()
    return results

def main():
    db_name = 'files.db'  # Database name
    print("Please select an option:")
    print("1. Insert files (scan directory)")
    print("2. Query database")
    choice = input("Enter option number (1 or 2): ")
    if choice == '1':
        directory = input("Enter the directory path to scan: ")
        extensions_input = input("Enter the file extensions to include (comma-separated, e.g., .txt,.py): ")
        extensions = tuple(ext.strip() for ext in extensions_input.split(','))
        files = get_all_files(directory, extensions)
        data = []
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            title = os.path.basename(file_path)
            data.append((title, content))
        insert_into_db(db_name, data)
        print("All files have been successfully inserted into the database.")
    elif choice == '2':
        keyword = input("Enter the keyword to search: ")
        results = query_db(db_name, keyword)
        if results:
            for id, title, content, in_title, occurrences in results:
                print(f"ID: {id}")
                print(f"Title: {title}")
                if in_title:
                    print("Keyword found in title.")
                print(f"Keyword occurrences in content: {int(occurrences)}")
                print(f"Content:\n{content}")
                print('='*40)
        else:
            print("No matching records found.")
    else:
        print("Invalid option.")

if __name__ == '__main__':
    main()
