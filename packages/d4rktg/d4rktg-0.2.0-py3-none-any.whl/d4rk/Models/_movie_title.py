# src/models/_movie_title.py

# from rapidfuzz import process

class FindMovie:
    def __init__(self):
        self.movie_titles = []
        self.movie_docs = []
    
    # def load_movie_titles(self, titles :list):
    #     self.movie_docs = titles
    #     self.movie_titles = [doc["title"] for doc in self.movie_docs]

    # def get_match_one(self,user_input):
    #     match, _, _ = process.extractOne(user_input, self.movie_titles)
    #     return match

    # def get_match_doc(self,match):
    #     return next((doc for doc in self.movie_docs if doc["title"] == match), None)
    
    # def get_match(self, user_input :str,limit :int=3):
    #     matches = process.extract(user_input, self.movie_titles, limit=limit)
    #     return matches

movie_finder = FindMovie()

