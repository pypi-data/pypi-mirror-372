
import cv2
import numpy as np
import pickle
from skimage.feature import hog, local_binary_pattern

class ImageClassifier:
    def __init__(self, model_path="best_model.pkl", use_grayscale=True):
        with open(model_path, "rb") as f:
            model_data = pickle.load(f)

        # Load stored parameters
        self.method = model_data["method"]
        self.object_features, self.not_object_features = model_data["features"]
        self.resize_size = model_data["resize_size"]
        self.score = model_data["score"]

        self.use_grayscale = use_grayscale  # ✅ new toggle

        # Register methods
        self.methods = {
            "ORB": {"extract": self.extract_orb, "classify": self.classify_orb},
            "HOG": {"extract": self.extract_hog, "classify": self.classify_cosine},
            "LBP": {"extract": self.extract_lbp, "classify": self.classify_cosine}
        }

        if self.method not in self.methods:
            raise ValueError(f"Unknown method '{self.method}' in model file")

        self.extract_fn = self.methods[self.method]["extract"]
        self.classify_fn = self.methods[self.method]["classify"]

    # --- Image preprocessing ---
    def preprocess(self, img):
        if img is None:
            return None
        img = cv2.resize(img, self.resize_size)

        if self.use_grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # ✅ grayscale option

        return img

    # --- Feature extractors ---
    def extract_orb(self, img, max_features=500):
        if len(img.shape) == 3:  # still color
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        orb = cv2.ORB_create(nfeatures=max_features)
        kp, des = orb.detectAndCompute(gray, None)
        return des

    def extract_hog(self, img):
        if len(img.shape) == 3:  # still color
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        return hog(gray, pixels_per_cell=(16, 16), cells_per_block=(2, 2), feature_vector=True)

    def extract_lbp(self, img, P=8, R=1):
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        lbp = local_binary_pattern(gray, P, R, method="uniform")
        hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, P + 3), range=(0, P + 2))
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-7)
        return hist

    # --- Classifiers ---
    def shape_similarity(self, des1, des2):
        if des1 is None or des2 is None:
            return 0.0
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        good_matches = [m for m in matches if m.distance < 50]
        return len(good_matches) / max(len(des1), len(des2))

    def classify_orb(self, img, object_features, not_object_features):
        des = self.extract_orb(img)
        max_obj_sim = max([self.shape_similarity(des, ref) for ref in object_features], default=0)
        max_not_sim = max([self.shape_similarity(des, ref) for ref in not_object_features], default=0)
        return 1 if max_obj_sim >= max_not_sim else 0

    def classify_cosine(self, img, object_features, not_object_features, extract_fn):
        feat = extract_fn(img)
        obj_sims = [np.dot(feat, f) / (np.linalg.norm(feat) * np.linalg.norm(f)) for f in object_features]
        not_sims = [np.dot(feat, f) / (np.linalg.norm(feat) * np.linalg.norm(f)) for f in not_object_features]
        max_obj_sim = max(obj_sims, default=0)
        max_not_sim = max(not_sims, default=0)
        return 1 if max_obj_sim >= max_not_sim else 0

    # --- Prediction API ---
    def predict(self, img):
        img = self.preprocess(img)
        if img is None:
            raise ValueError("Invalid image provided (None)")

        if self.method == "ORB":
            return self.classify_fn(img, self.object_features, self.not_object_features)
        else:
            return self.classify_fn(img, self.object_features, self.not_object_features, self.extract_fn)


# --- Example usage ---
if __name__ == "__main__":
    model = MLModel("best_model.pkl", use_grayscale=True)  # ✅ toggle grayscale here
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        pred = model.predict(frame)
        label = "OBJECT" if pred == 1 else "NOT OBJECT"
        cv2.putText(frame, label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Live Inference", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
