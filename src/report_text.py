"""Final report wording, written for the results in results/*.json (Muhammad Uzair, roll 231101).
Edit freely - these are plain strings. report_builder.py inserts them into the Word files."""

# ------------------------------------------------------------------ Q1
Q1_CHOICES = [
    "Feature scaling – standardisation: z = (x − mean) / std, learned from the 16 training rows only so that no test information leaks in. Age and experience have very different ranges; "
    "with standardisation gradient descent got within 1 % of the optimal cost in 8 iterations, with min-max scaling in 139 iterations, and without scaling it had still not got there after 5000.",
    "Learning rate α = 0.1: in the learning-rate experiment this value reached the final cost (about 2.95 million) within 300 iterations without oscillating, and it is well below the value (α = 3) where the cost diverges.",
    "Regularisation λ = 1.0: a moderate value chosen to demonstrate the effect of regularisation. The λ sweep shows that for this very small dataset smaller values (0 to 0.1) give a lower test error, so λ = 1 is on the strong side.",
    "Iterations = 2000: the cost stops changing after about 300 iterations, so 2000 is more than enough; the result matches the closed-form solution to about 3×10⁻¹¹.",
    "Dataset size: the file has only 20 rows (16 training, 4 test), so all test errors are noisy and the experiments should be read as demonstrations, not precise estimates.",
]

Q1_LAMBDA_NOTE = ("Note: for λ = 1000 and λ = 10000 gradient descent with α = 0.1 did not converge (the gap to the closed-form solution is huge, about 10¹⁴, and the MSE is about 10²⁹–10³¹). "
                  "With only 16 training rows the update becomes unstable when α·λ/m is above about 2, so those two rows are not valid results; the valid under-fitting evidence is λ = 10 and λ = 100.")

Q1_DISCUSSION = [
    ("Learning rate",
     "The learning rate α sets the step size of gradient descent. With α = 0.001 the cost after 300 iterations was still about 513 million, because the steps were too small. "
     "With α = 0.01 it was 5.46 million and with α = 0.03 it was 2,954,196, close to the minimum. The values 0.1, 0.3 and 1.0 all reached the final cost of 2,953,974 within 300 iterations. "
     "With α = 3.0 the steps overshot the minimum and the cost exploded to about 4×10³⁰ (divergence). So α must be large enough to be fast but below the stability limit. I used α = 0.1."),
    ("Feature scaling",
     "Age and experience have very different ranges, which stretches the cost surface and forces a tiny learning rate. Without scaling the largest stable α was only 0.0005, and after 5000 iterations "
     "the test MSE was still 91.8 million against the optimal 753,797. With min-max scaling the largest stable α was 0.72 and 139 iterations were needed; with standardisation it was 0.68 and only 8 iterations. "
     "All scaled versions reached the same optimum, so scaling changes the speed of convergence, not the final answer."),
    ("Regularisation λ, under-fitting and over-fitting",
     "As λ increased from 0 to 0.01, 0.1, 1, 10 and 100, the test MSE grew from 753,797 to 755,622, 772,534, 990,779, 6,947,102 and 52,985,224, the weight norm fell from 8,511 to 1,144, and the training MSE also rose "
     "(12.3 million at λ = 10 and 49.2 million at λ = 100). Both errors being high means under-fitting (high bias). "
     "For λ = 1000 and 10000 gradient descent did not converge (see the note under the table), so those rows are not valid results. "
     "The original model cannot over-fit much because it has only two features, so I ran a stress test with degree-3 polynomial features (10 parameters) and only 16 training rows. "
     "With λ = 0 the training MSE was 274,785 but the test MSE was 5,640,428, about 20 times larger – clear over-fitting (high variance). "
     "With λ = 0.01 the test MSE fell to 1,145,810, about five times lower, and larger values of λ started to under-fit again."),
    ("Comparison with scikit-learn",
     "With λ = 0 my gradient descent gave a test MSE of 753,796.77, the same as scikit-learn's LinearRegression, and the coefficients agreed (intercept 31,465.06, age −101.06, experience 2,154.81). "
     "It also matched the closed-form solution to 3×10⁻¹¹, which shows the implementation is correct. With λ = 1 the test MSE was 990,779 (R² 0.919 against 0.939) and the age and experience coefficients shrank to −62.9 and 1,990.8; "
     "this is the expected bias introduced by regularisation. scikit-learn was faster (0.016 s against 0.203 s for 2000 iterations) because it solves the problem directly instead of iterating."),
    ("Limitations",
     "The dataset has only 20 rows and the test set only 4 points, so every test error is noisy. The results demonstrate the behaviour of the algorithm but should not be read as precise performance estimates."),
]

# ------------------------------------------------------------------ Q2
Q2_PART_A = [
    ("Ingredient 1 – the strength of the individual trees.",
     "Strength tells how reliable a single tree is. If every tree is only slightly better than guessing, a vote of many such trees is still weak. Strong trees vote correctly with a clear margin on most inputs, "
     "so the ensemble error is low. Breiman's bound, PE* ≤ ρ̄ (1 − s²) / s², shows that the error grows as the strength s decreases."),
    ("Ingredient 2 – low correlation between the trees.",
     "If all trees make the same mistakes, voting cancels nothing. For N predictors with variance σ² and average correlation ρ, the variance of their average is ρσ² + (1 − ρ)σ²/N. "
     "Adding trees removes only the second term, so the remaining error is set by the correlation ρ. Random forests lower ρ by training each tree on a different bootstrap sample and by letting each split choose from a random subset of the features."),
    ("How the two interact (trade-off).",
     "A smaller random feature subset lowers the correlation but also weakens each tree; using all features gives strong but highly correlated trees. The best forest balances the two, which is why max_features is an important setting."),
    ("Why combining many trees improves stability and performance.",
     "A fully grown tree has low bias but high variance, because small changes in the data give a very different tree. Averaging many different trees keeps the low bias and cuts the variance, "
     "so predictions are more accurate and more repeatable. Breiman proved that the generalisation error converges as trees are added, so more trees do not cause over-fitting – they only cost time."),
]

Q2_HEART_NOTE = ("Note: all 13 columns of this file are already numeric (sex, cp, thal etc. are coded as numbers) and there are no missing values, so in practice only standardisation was applied and no one-hot encoding was needed.")

Q2_DISCUSSION = [
    ("Effect of the number of trees on accuracy and stability",
     "On Heart Disease the mean test accuracy rose from 0.743 with 1 tree to 0.837 with 10 trees and about 0.85 from 50 trees on (0.847 with 300 trees). The spread across the five seeds was 0.048 at 1 tree, "
     "peaked at 0.059 at 10 trees and fell to 0.012 with 100 trees and 0.014 with 300. On Intel Images accuracy rose from 0.404 to 0.528 (10 trees), 0.591 (50), 0.606 (100) and 0.614 (300), and the spread shrank from 0.009 to about 0.004. "
     "Most of the gain comes in the first 50 trees, after which the curve flattens, so extra trees mainly buy stability. Training accuracy was already about 1.0 from 50 trees while the test and out-of-bag accuracy (about 0.80 on Heart) stayed stable, "
     "so more trees did not cause over-fitting, in line with Breiman's convergence result."),
    ("Random Forest versus a single tree",
     "On Heart Disease the default forest reached 0.883 accuracy and 0.945 ROC-AUC against 0.783 and 0.779 for the single tree, but it needed 0.330 s to train against 0.003 s. "
     "On Intel Images the forest reached 0.601 accuracy against 0.446. Here the forest trained faster (about 79 s against 153 s; the sweep measured about 34 s for 100 trees, so timings vary on my laptop), "
     "because a single unrestricted tree searches all 3072 pixel features at every split, while each forest split searches only about 55 random ones and the trees are built in parallel."),
    ("Comparison with SVM and the effect of tuning",
     "On the Heart test set the SVM scored 0.900 accuracy, the forest 0.883 and the tree 0.783. With only 60 test patients the gap between SVM and forest is one patient, so the 5-fold cross-validation is more reliable: "
     "Decision Tree 0.741 ± 0.059, Random Forest 0.815 ± 0.052, SVM 0.825 ± 0.055. The forest and the SVM are very close and both clearly beat the tree. "
     "Tuning with GridSearchCV did not improve the test split: the tuned tree (max_depth 3) got 0.767, the forest stayed at 0.883 and the SVM fell to 0.867. "
     "On Intel Images the SVM again came first (0.648), then the forest (0.601) and the tree (0.446), but its prediction was much slower (13.5 s for 3000 images against 0.25 s for the forest) because the RBF kernel compares every image with many support vectors."),
    ("What the models learned",
     "On Heart Disease the most important features of the forest were thalach (0.159), cp (0.123), oldpeak (0.115) and ca (0.109). On Intel Images the forest was best for forest scenes (F1 0.76) and weakest for buildings and sea (F1 0.45 and 0.48), "
     "classes that look alike in raw colour pixels."),
    ("Insights on randomness and ensemble size, and limitations",
     "Randomness (bootstrap samples and random feature subsets) is what makes the trees different from each other. About 100 trees is usually enough; 300 trees cost three times the training time for little extra accuracy. "
     "On raw 32×32 pixels all models are limited by the weak features (the forest reaches almost 100 % training accuracy but only about 61 % test accuracy), so a CNN or engineered features such as HOG would be needed for a big improvement. "
     "The results come from one split per dataset and, for Heart Disease, only 60 test patients."),
]

# ------------------------------------------------------------------ Q3
Q3_DISCUSSION = [
    "On the same test set the baseline Logistic Regression reached ROC-AUC 0.909, accuracy 0.857, precision 0.744, recall 0.619 and F1 0.675. The TPOT pipeline reached ROC-AUC 0.879, accuracy 0.748, precision 0.486, recall 0.860 and F1 0.621. "
    "TPOT's final model was a Bernoulli Naive Bayes with fit_prior=False, which ignores the class imbalance (roughly 76 % earn ≤50K) and therefore predicts '>50K' much more often; that explains its high recall and low precision. "
    "TPOT's search took 2012 seconds (about 33.5 minutes), while the baseline trained in 1.7 seconds, more than 1000 times faster. The baseline also predicts faster (0.011 against 0.066 ms per row) and is smaller "
    "(0.009 MB with 106 coefficients against 0.100 MB for a multi-step pipeline). On this task the simple baseline was better on almost every measure, so I deployed it. TPOT only wins on recall, which would matter if missing a high earner were the most costly error.",
    "AutoML is useful because it tries many models and settings automatically. However, with a 30-minute budget, a light search space and a scorer based on cross-validated ROC-AUC (it does not tune the decision threshold), it is not guaranteed to beat a well-engineered baseline. "
    "Its drawbacks are the long search time, lower reproducibility and a harder-to-explain pipeline.",
    "The most important features of the deployed model (permutation importance, drop in ROC-AUC) were marital_status (0.096), capital_gain (0.038), age (0.033), education_num (0.030) and occupation (0.016).",
    "Limitations: the best model was chosen on the test set, which is slightly optimistic, and only one train/test split was used. Possible improvements: a longer TPOT search, class weights, tuning the decision threshold and a separate validation set.",
]
