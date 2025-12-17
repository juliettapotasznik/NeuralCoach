import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer
import faiss
from UserProfile import UserProfile


class RecipeRAG:

    def __init__(self,
                 csv_path: str,
                 embeddings_cache_path: str = None,
                 index_cache_path: str = None):

        self.csv_path = csv_path

        # If cache paths not provided, use the same directory as the CSV file
        if embeddings_cache_path is None:
            csv_dir = os.path.dirname(os.path.abspath(csv_path))
            embeddings_cache_path = os.path.join(csv_dir, 'recipe_embeddings.npy')

        if index_cache_path is None:
            csv_dir = os.path.dirname(os.path.abspath(csv_path))
            index_cache_path = os.path.join(csv_dir, 'recipe_index.faiss')

        self.embeddings_cache_path = embeddings_cache_path
        self.index_cache_path = index_cache_path

        # ładowanie danych przepisów
        self.df = pd.read_csv(csv_path)
        print(f" Załadowano {len(self.df)} przepisów")

        # incializowanie modelu embeddingów
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # ładowanie lub tworzenie embeddingów
        if os.path.exists(embeddings_cache_path) and os.path.exists(index_cache_path):
            self.embeddings = np.load(embeddings_cache_path)
            self.index = faiss.read_index(index_cache_path)
            print(f"   Załadowano {len(self.embeddings)} embeddings z cache")
        else:
            print("Tworzenie embeddings")
            self._create_embeddings()
            print("Embeddings utworzone i zapisane")

    def _create_embeddings(self):
        # Generowanie embeddingów dla przepisów
        recipe_texts = []
        for _, row in self.df.iterrows():
            text = f"{row['recipe_name']}. "
            text += f"Cuisine: {row['primary_cuisine']}. "
            text += f"Meal type: {row['meal_slot']}. "

            # Dodaj informacje dietetyczne
            dietary = []
            if row['is_vegetarian']:
                dietary.append('vegetarian')
            if row['is_vegan']:
                dietary.append('vegan')
            if row['is_gluten_free']:
                dietary.append('gluten-free')
            if dietary:
                text += f"Diet: {', '.join(dietary)}. "

            # Dodaj wartości odżywcze
            text += f"Calories: {row['calories_per_serving']}. "
            text += f"Protein: {row['protein_per_serving']}g. "

            # Dodaj składniki
            if pd.notna(row['ingredient_names']):
                ingredients = row['ingredient_names'].replace('|', ', ')
                text += f"Ingredients: {ingredients}."

            recipe_texts.append(text)

        # Generowanie embeddingów
        self.embeddings = self.embedding_model.encode(
            recipe_texts,
            show_progress_bar=True,
            batch_size=32
        )

        # Tworzenie indeksu FAISS
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))

        # Zapis do cache
        np.save(self.embeddings_cache_path, self.embeddings)
        faiss.write_index(self.index, self.index_cache_path)

    def filter_recipes(self, user: UserProfile) -> pd.DataFrame:
        """
        Filter recipes based on user preferences
        """
        df_filtered = self.df.copy()

        # Ograniczenia dietetyczne
        if user.diet:
            diet = user.diet.lower().replace('-', '_')

            if diet == 'vegetarian':
                df_filtered = df_filtered[df_filtered['is_vegetarian'] == True]
            elif diet == 'vegan':
                df_filtered = df_filtered[df_filtered['is_vegan'] == True]
            elif diet == 'gluten_free':
                df_filtered = df_filtered[df_filtered['is_gluten_free'] == True]
            elif diet == 'dairy_free':
                df_filtered = df_filtered[df_filtered['is_dairy_free'] == True]
            elif diet == 'soy_free':
                df_filtered = df_filtered[df_filtered['is_soy_free'] == True]
            elif diet == 'nuts_free':
                df_filtered = df_filtered[
                    (df_filtered['is_tree_nut_free'] == True) &
                    (df_filtered['is_peanut_free'] == True)
                ]
            elif diet == 'eggs_free':
                df_filtered = df_filtered[df_filtered['is_egg_free'] == True]
            elif diet == 'shellfish_free':
                df_filtered = df_filtered[df_filtered['is_shellfish_free'] == True]

        # Nietolerancje (ta sama logika co dieta)
        if user.intolerances:
            # Obsługa zarówno stringa, jak i listy
            intolerances_list = user.intolerances if isinstance(user.intolerances, list) else [user.intolerances]

            for intolerance_item in intolerances_list:
                intolerance = intolerance_item.lower().replace('-', '_')

                if intolerance == 'gluten':
                    df_filtered = df_filtered[df_filtered['is_gluten_free'] == True]
                elif intolerance == 'dairy':
                    df_filtered = df_filtered[df_filtered['is_dairy_free'] == True]
                elif intolerance == 'soy':
                    df_filtered = df_filtered[df_filtered['is_soy_free'] == True]
                elif intolerance == 'nuts':
                    df_filtered = df_filtered[
                        (df_filtered['is_tree_nut_free'] == True) &
                        (df_filtered['is_peanut_free'] == True)
                    ]
                elif intolerance == 'eggs':
                    df_filtered = df_filtered[df_filtered['is_egg_free'] == True]
                elif intolerance == 'shellfish':
                    df_filtered = df_filtered[df_filtered['is_shellfish_free'] == True]
                else:
                    # Dla innych nietolerancji, filtruj po nazwie składnika LUB tytule przepisu
                    intolerance_lower = intolerance.lower()

                    # Jeśli masz kolumnę ingredient_names
                    if 'ingredient_names' in df_filtered.columns:
                        df_filtered = df_filtered[
                            ~(
                                df_filtered['ingredient_names'].str.lower().str.contains(intolerance_lower, na=False) |
                                df_filtered['recipe_name'].str.lower().str.contains(intolerance_lower, na=False)
                            )
                        ]

                    # Jeśli masz kolumnę ingredients_text
                    elif 'ingredients_text' in df_filtered.columns:
                        df_filtered = df_filtered[
                            ~(
                                df_filtered['ingredients_text'].str.lower().str.contains(intolerance_lower, na=False) |
                                df_filtered['recipe_name'].str.lower().str.contains(intolerance_lower, na=False)
                            )
                        ]

                    else:
                        df_filtered = df_filtered[
                            ~df_filtered['recipe_name'].str.lower().str.contains(intolerance_lower, na=False)
                        ]

        # Macro profile
        if user.macro_profile:
            profile = user.macro_profile.lower().replace('-', '_')

            if profile == 'balanced':
                df_filtered = df_filtered[df_filtered['is_balanced'] == True]
            elif profile == 'high_fiber':
                df_filtered = df_filtered[df_filtered['is_high_fiber'] == True]
            elif profile == 'high_protein':
                df_filtered = df_filtered[df_filtered['is_high_protein'] == True]
            elif profile == 'low_carb':
                df_filtered = df_filtered[df_filtered['is_low_carb'] == True]
            elif profile == 'low_fat':
                df_filtered = df_filtered[df_filtered['is_low_fat'] == True]
            elif profile == 'low_sodium':
                df_filtered = df_filtered[df_filtered['is_low_sodium'] == True]

        # Preferowane składniki
        if user.prefer_ingredients:
            preferred = [ing.lower() for ing in user.prefer_ingredients]
            # Sprawdzanie zarówno w ingredients_text, jak i ingredient_names
            if 'ingredients_text' in df_filtered.columns:
                df_filtered = df_filtered[
                    df_filtered['ingredients_text'].apply(
                        lambda x: any(pref in str(x).lower() for pref in preferred)
                    )
                ]
            elif 'ingredient_names' in df_filtered.columns:
                df_filtered = df_filtered[
                    df_filtered['ingredient_names'].apply(
                        lambda x: any(pref in str(x).lower() for pref in preferred)
                    )
                ]

        return df_filtered

    def search_similar_recipes(self,
                               query: str,
                               filtered_df: pd.DataFrame,
                               k: int = 10) -> pd.DataFrame:
        # Kodowanie zapytania
        query_embedding = self.embedding_model.encode([query])[0]

        # Pobierz indeksy przefiltrowanych przepisów
        filtered_indices = filtered_df.index.tolist()

        if len(filtered_indices) == 0:
            return pd.DataFrame()

        # Wyszukiwanie w przefiltrowanym podzbiorze
        filtered_embeddings = self.embeddings[filtered_indices]

        # Tworzenie tymczasowego indeksu dla przefiltrowanych embeddingów
        temp_index = faiss.IndexFlatL2(filtered_embeddings.shape[1])
        temp_index.add(filtered_embeddings.astype('float32'))

        # Wyszukiwanie podobnych przepisów
        k = min(k, len(filtered_indices))
        distances, indices = temp_index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            k
        )

        # Mapowanie z powrotem do oryginalnych indeksów DataFrame
        original_indices = [filtered_indices[i] for i in indices[0]]

        return self.df.iloc[original_indices]
