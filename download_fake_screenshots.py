from icrawler.builtin import GoogleImageCrawler

# Folder to save images
output_dir = "dataset/fake"  
search_terms = [
    "fake gpay transaction screenshot",
    "fake phonepe payment screenshot",
    "fake paytm payment screenshot",
    "spoofed payment receipt",
    "edited gpay receipt",
    "scam transaction screenshot"
]

for term in search_terms:
    print(f"🔍 Downloading for: {term}")
    google_crawler = GoogleImageCrawler(storage={'root_dir': output_dir})
    google_crawler.crawl(keyword=term, max_num=20, file_idx_offset='auto')
