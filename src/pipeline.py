import pickle
import pandas as pd

from datetime import datetime

from metaflow import FlowSpec, step

# Choose regressor as we need to pick 2 papers
# so we can sort it by probability and choose the first 2
from sklearn.ensemble import GradientBoostingRegressor 
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict

from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer

class XGBoostPipeline(FlowSpec):
    def datapipeline(self, data):
        data = data.dropna(subset=["label"])
        
        count_vec = CountVectorizer()

        ab_counts = count_vec.fit_transform(data["abstract"])
        ti_counts = count_vec.fit_transform(data["title"])
        
        # TF transform
        ab_transformer = TfidfTransformer(use_idf=False).fit(ab_counts)
        ti_transformer = TfidfTransformer(use_idf=False).fit(ti_counts)

        ab_tf = ab_transformer.transform(ab_counts)
        ti_tf = ti_transformer.transform(ti_counts)

        # Apply PCA
        pca = PCA(n_components=3)
        pca_ab = pca.fit_transform(ab_tf.toarray())
        pca_ti = pca.fit_transform(ti_tf.toarray())

        data["PCA1_abstract"] = pca_ab[:, 0]
        data["PCA2_abstract"] = pca_ab[:, 1]
        data["PCA3_abstract"] = pca_ab[:, 2]
        data["PCA1_title"]    = pca_ti[:, 0]
        data["PCA2_title"]    = pca_ti[:, 1]
        data["PCA3_title"]    = pca_ti[:, 2]
        
        return data
        
    @step
    def start(self):
        df = pd.read_json(r"./data/final/data_30-01-2024_mr_2000_edited.json")
        
        self.test_col  = ["PCA1_abstract", "PCA2_abstract", "PCA3_abstract", "PCA1_title", "PCA2_title", "PCA3_title"]
        self.label_col = "label"

        df = self.datapipeline(df)

        # Split data into training and testing sets
        self.train_data, self.test_data = train_test_split(df, test_size=0.2, random_state=42)

        self.next(self.train_model)

    @step
    def train_model(self):
        # Train on PCA features
        train_features = self.train_data[self.test_col]
        train_labels   = self.train_data[self.label_col]

        model = GradientBoostingRegressor()
        model.fit(train_features, train_labels)

        self.model = model

        self.next(self.evaluate_model)

    @step
    def evaluate_model(self):
        # Evaluate
        test_features = self.test_data[self.test_col]
        test_labels   = self.test_data[self.label_col]

        predictions = self.model.predict(test_features)
        mse = mean_squared_error(test_labels, predictions)
        
        print("Model MSE:", mse)
        
        current_date   = datetime.now().strftime("%d-%m-%Y")
        model_filename = f"model/xgboost_{current_date}.pkl"

        # Pickle model file
        with open(model_filename, "wb") as file:
            pickle.dump(self.model, file)

        self.next(self.cross_validation)

    @step
    def cross_validation(self):
        # Perform stratified 10-fold cross-validation
        skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
        cross_val_features = self.train_data[self.test_col]
        cross_val_labels   = self.train_data[self.label_col]

        # Use cross_val_predict to get predictions for each fold
        cross_val_predictions = cross_val_predict(self.model, cross_val_features, cross_val_labels, cv=skf)

        # Print cross-validation metrics
        print("Cross-Validation Metrics:")
        print("Mean Squared Error:", mean_squared_error(cross_val_labels, cross_val_predictions))
        print("R-squared:", r2_score(cross_val_labels, cross_val_predictions))

        self.cross_val_predictions = cross_val_predictions

        self.next(self.test)

    @step
    def test(self):
        # Take the first three entries from the test data
        sample_test_data = self.test_data.head(3)

        # Extract PCA features for the sample test data
        test_features = sample_test_data[self.test_col]

        # Make predictions
        predictions = self.model.predict(test_features)

        # Print the sample test data and predictions
        for i, (title, abstract, label, prediction) in \
            enumerate(zip(sample_test_data["title"], sample_test_data["abstract"], 
                          sample_test_data["label"], predictions), start=1):
                
            print(f"\nSample Test Data {i}:")
            print(f"Title:      {title}")
            print(f"Abstract:   {abstract}")
            print(f"Label:      {label}")
            print(f"Prediction: {prediction}")

        self.next(self.end)

    @step
    def end(self):
        print("Done!")

if __name__ == "__main__":
    XGBoostPipeline()
