
import time
import cv2
import numpy as np
import os
import random
import pickle
from skimage.feature import hog, local_binary_pattern

class ImageClassifierTrainer:
    def __init__(self, dataset_path, method=4, n_runs=5,
                 resize_size=(128, 128), model_path="best_model.pkl", use_grayscale=True):
        self.dataset_path = dataset_path
        self.method = method
        self.n_runs = n_runs
        self.resize_size = resize_size
        self.model_path = model_path
        self.use_grayscale = use_grayscale  # ✅ grayscale toggle

        self.methods = {
            "ORB": {"extract": self.extract_orb, "classify": self.classify_orb},
            "HOG": {"extract": self.extract_hog, "classify": self.classify_cosine},
            "LBP": {"extract": self.extract_lbp, "classify": self.classify_cosine}
        }

        # --- discover classes dynamically
        self.classes = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
        self.classes.sort()
        print(f"[INFO] Found classes: {self.classes}")

    # --- Model save/load ---
    def save_model(self, method_name, features, score):
        model_data = {
            "method": method_name,
            "features": features,   # dict: {class_name: [features]}
            "classes": self.classes,
            "resize_size": self.resize_size,
            "score": score,
            "use_grayscale": self.use_grayscale
        }
        with open(self.model_path, "wb") as f:
            pickle.dump(model_data, f)
        print(f"[MODEL SAVED] {method_name} with score {score:.2f}")

    def load_model(self):
        if not os.path.exists(self.model_path):
            return None
        with open(self.model_path, "rb") as f:
            return pickle.load(f)

    # --- Image loading ---
    def load_and_prepare_image(self, path):
        img = cv2.imread(path)
        if img is None:
            return None
        img = cv2.resize(img, self.resize_size)
        if self.use_grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    # --- Feature extraction ---
    def extract_orb(self, img, max_features=500):
        if len(img.shape) == 3:  # safety
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create(nfeatures=max_features)
        kp, des = orb.detectAndCompute(img, None)
        return des

    def extract_hog(self, img):
        if len(img.shape) == 3:  # safety
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = hog(img, pixels_per_cell=(16, 16), cells_per_block=(2, 2), feature_vector=True)
        return features

    def extract_lbp(self, img, P=8, R=1):
        if len(img.shape) == 3:  # safety
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lbp = local_binary_pattern(img, P, R, method="uniform")
        hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, P + 3), range=(0, P + 2))
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-7)
        return hist

    # --- Classification ---
    def shape_similarity(self, des1, des2):
        if des1 is None or des2 is None:
            return 0.0
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        good_matches = [m for m in matches if m.distance < 50]
        return len(good_matches) / max(len(des1), len(des2))

    def classify_orb(self, img, class_features):
        des = self.extract_orb(img)
        sims = {}
        for cname, feats in class_features.items():
            sims[cname] = max([self.shape_similarity(des, ref) for ref in feats], default=0)
        return max(sims, key=sims.get)  # return best class

    def classify_cosine(self, img, class_features, extract_fn):
        feat = extract_fn(img)
        sims = {}
        for cname, feats in class_features.items():
            vals = [np.dot(feat, f) / (np.linalg.norm(feat) * np.linalg.norm(f)) for f in feats]
            sims[cname] = max(vals, default=0)
        return max(sims, key=sims.get)

    # --- Precompute ---
    def precompute_features(self, folder_path, extract_fn, fraction=0.8):
        all_images = os.listdir(folder_path)
        n_sample = max(1, int(len(all_images) * fraction))
        sampled_images = random.sample(all_images, n_sample)
        features, used_names = [], []
        for img_name in sampled_images:
            img = self.load_and_prepare_image(os.path.join(folder_path, img_name))
            if img is None:
                continue
            features.append(extract_fn(img))
            used_names.append(img_name)
        return features, used_names

    # --- Evaluation ---
    def evaluate(self, method_name, classify_fn, test_images, class_features, extract_fn=None):
        results = []
        start = time.perf_counter()
        for img_name, true_class, folder in test_images:
            img_path = os.path.join(folder, img_name)
            img = self.load_and_prepare_image(img_path)
            if img is None:
                continue
            if method_name == "ORB":
                pred_class = classify_fn(img, class_features)
            else:
                pred_class = classify_fn(img, class_features, extract_fn)
            results.append(pred_class == true_class)
        end = time.perf_counter()
        accuracy = np.mean(results)
        avg_time = (end-start)/len(test_images)
        fps = 1/avg_time
        print(f"\n[{method_name}] Accuracy: {accuracy*100:.2f}%")
        print(f"[{method_name}] Avg time per frame: {avg_time:.6f} s")
        print(f"[{method_name}] Approx FPS: {fps:.1f}")
        return [fps, avg_time, accuracy]

    # --- Scoring ---
    def calculate_score(self, eval_params):
        return ((eval_params[0] * 1.5) + (eval_params[2] * 2)) / eval_params[1] ** 2

    # --- Run training ---
    def fit(self):
        chosen_methods = []
        if self.method == 1:
            chosen_methods = ["HOG"]
        elif self.method == 2:
            chosen_methods = ["ORB"]
        elif self.method == 3:
            chosen_methods = ["LBP"]
        elif self.method == 4:
            chosen_methods = list(self.methods.keys())
        else:
            raise ValueError("Method must be 1=HOG, 2=ORB, 3=LBP, 4=All")

        total_eval = {m: np.zeros(3) for m in chosen_methods}
        best_scores = {m: 0 for m in chosen_methods}
        global_best = -float("inf")

        for run in range(1, self.n_runs+1):
            print(f"\n--- RUN {run} ---")
            method_features, used_names = {}, {}

            for name in chosen_methods:
                class_feats, class_used = {}, {}
                for cname in self.classes:
                    folder_path = os.path.join(self.dataset_path, cname)
                    feats, names = self.precompute_features(folder_path, self.methods[name]["extract"])
                    class_feats[cname] = feats
                    class_used[cname] = names
                method_features[name] = class_feats
                used_names[name] = class_used

            # build test set
            test_images = []
            def get_test_images(folder_path, used_names, cname, fraction=0.2):
                all_images = [f for f in os.listdir(folder_path) if f not in used_names]
                n_test = max(1, int(len(all_images) * fraction))
                return [(f, cname, folder_path) for f in random.sample(all_images, n_test)]

            for cname in self.classes:
                folder = os.path.join(self.dataset_path, cname)
                test_images.extend(get_test_images(folder, used_names[name][cname], cname))

            # Evaluate
            for name in chosen_methods:
                eval_res = self.evaluate(name, self.methods[name]["classify"],
                                         test_images, method_features[name], self.methods[name]["extract"])
                total_eval[name] += np.array(eval_res)
                score = self.calculate_score(eval_res)

                if score > best_scores[name]:
                    best_scores[name] = score

                if score > global_best:
                    global_best = score
                    self.save_model(name, method_features[name], score)

        # Average results
        print("\n=== FINAL AVERAGED RESULTS ===")
        avg_scores = {m: self.calculate_score(total_eval[m]/self.n_runs) for m in chosen_methods}
        for name in chosen_methods:
            print(f"{name}: FPS={total_eval[name][0]/self.n_runs:.1f}, "
                  f"Time={total_eval[name][1]/self.n_runs:.6f}, "
                  f"Acc={total_eval[name][2]/self.n_runs:.2f}, "
                  f"Score={avg_scores[name]:.2f}")

        if self.method == 4:
            best = max(avg_scores, key=avg_scores.get)
            print(f"\nBest method overall: {best}")
            return best, avg_scores[best]

        return chosen_methods[0], avg_scores[chosen_methods[0]]
