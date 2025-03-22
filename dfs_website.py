import requests
from bs4 import BeautifulSoup
import mysql.connector

# Koneksi ke database MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="website_db"
)
cursor = conn.cursor()

# Buat tabel jika belum ada
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255),
        title VARCHAR(255),
        paragraph TEXT
    )
""")

# Fungsi DFS untuk menjelajahi halaman web
def dfs_scrape(url, visited):
    if url in visited:
        return
    visited.add(url)
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return
    except requests.exceptions.RequestException:
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else "No Title"
    paragraph = soup.find('p').text if soup.find('p') else "No Content"

    # Simpan ke database
    cursor.execute("INSERT INTO pages (url, title, paragraph) VALUES (%s, %s, %s)", (url, title, paragraph))
    conn.commit()
    
    # Cari semua link dalam halaman
    for link in soup.find_all('a', href=True):
        next_url = f"http://localhost:8000/{link['href']}"
        dfs_scrape(next_url, visited)

# Jalankan DFS mulai dari index.html
dfs_scrape("http://localhost:8000/index.html", set())

# Tutup koneksi database
cursor.close()
conn.close()
