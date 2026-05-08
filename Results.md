# Results (As of 8th May BEFORE Version 6.6 Livestream)

Comparing results between the prediction model and the longest wait wins heuristic. 

Predictions for 6.6 are also shown, and will be updated after characters are confirmed by hoyo. 

## Predictions

Test set starts from version 5.0 and ends at version 6.5. In total, there are 41 rerun slots to guess. Testing starts from 5.0 to give the model some time to learn. 

The character column contains all rerun-ed characters for a patch. Correct predictions are <span style="color:green"> green</span>, missed predictions are <span style="color:red"> red</span>.


Chronicle banner characters couldn't be guessed after their last regular banner. Characters who are on the chronicle banner do not get regular rerun banners.



### Model Predictions

|Patch                   |Character                               |
|------------------------|----------------------------------------|
|5.0                     | <span style=color:red>Kaedehara Kazuha</span> / <span style=color:red>Raiden Shogun</span>|
|5.1                     | <span style=color:red>Nahida</span> / <span style=color:red>Hu Tao</span> / <span style=color:red>Chiori</span>|
|5.2                     | <span style=color:green>Lyney</span> / <span style=color:red>Zhongli</span> / <span style=color:red>Neuvillette</span>|
|5.3                     | <span style=color:green>Arlecchino</span> / <span style=color:green>Clorinde</span>|
|5.4                     | <span style=color:red>Furina</span> / <span style=color:green>Sigewinne</span> / <span style=color:red>Wriothesley</span>|
|5.5                     | <span style=color:red>Venti</span> / <span style=color:red>Xianyun</span> / <span style=color:red>Xilonen</span>|
|5.6                     | <span style=color:green>Kinich</span> / <span style=color:red>Navia</span> / <span style=color:green>Raiden Shogun</span>|
|5.7                     | <span style=color:green>Mavuika</span> / <span style=color:green>Emilie</span> / <span style=color:red>Shenhe</span>|
|5.8                     | <span style=color:red>Citlali</span> / <span style=color:green>Chasca</span> / <span style=color:green>Mualani</span>|
|6.0                     | <span style=color:red>Yelan</span> / <span style=color:red>Nahida</span>|
|6.1                     | <span style=color:green>Furina</span> / <span style=color:red>Zhongli</span> / <span style=color:red>Arlecchino</span>|
|6.2                     | <span style=color:red>Venti</span> / <span style=color:green>Varesa</span> / <span style=color:green>Xilonen</span>|
|6.3                     | <span style=color:red>Neuvillette</span> / <span style=color:green>Ineffa</span>|
|6.4                     | <span style=color:green>Skirk</span> / <span style=color:red>Escoffier</span> / <span style=color:green>Flins</span>|
|6.5                     | <span style=color:green>Chasca</span> / <span style=color:green>Lauma</span> / <span style=color:red>Nefer</span>|



Patch 5.0+
- Total Predicted: 41
- Correct Hits: 18
- Accuaracy: 43.90%

Patch 6.0+
- Total Predicted: 16
- Correct Hits: 8
- Accuracy: 50.00%

The model was trained on all patches before the one it was currently guessing, and guessed the top n probabilites for how many rerun slots there were for each patch. 

This logic lead to some constraint based success. For example, Lauma and Chasca were in the top 3 probabilites for patch 6.5, however, Chasca only had a individual probability rate of 0.15. In a vacuum, the model would not predict Chasca, but by being forced to, it actually led to a correct guess.  

### LWW Predictions

|Patch|Character                    |
|-----|-----------------------------|
|5.0  |<span style="color:red">Kaedehara Kazuha</span> / <span style="color:red">Raiden Shogun</span>|
|5.1  |<span style="color:red">Nahida</span> / <span style="color:green">Hu Tao</span> / <span style="color:red">Chiori</span>|
|5.2  |<span style="color:red">Lyney</span> / <span style="color:green">Zhongli</span> / <span style="color:red">Neuvillette</span>|
|5.3  |<span style="color:red">Arlecchino</span> / <span style="color:red">Clorinde</span>|
|5.4  |<span style="color:red">Furina</span> / <span style="color:red">Sigewinne</span> / <span style="color:green">Wriothesley</span>|
|5.5  |<span style="color:green">Venti</span> / <span style="color:green">Xianyun</span> / <span style="color:red">Xilonen</span>|
|5.6  |<span style="color:red">Kinich</span> / <span style="color:green">Navia</span> / <span style="color:red">Raiden Shogun</span>|
|5.7  |<span style="color:red">Mavuika</span> / <span style="color:green">Emilie</span> / <span style="color:red">Shenhe</span>|
|5.8  |<span style="color:red">Citlali</span> / <span style="color:red">Chasca</span> / <span style="color:green">Mualani</span>|
|6.0  |<span style="color:green">Yelan</span> / <span style="color:red">Nahida</span>|
|6.1  |<span style="color:red">Furina</span> / <span style="color:green">Zhongli</span> / <span style="color:red">Arlecchino</span>|
|6.2  |<span style="color:red">Venti</span> / <span style="color:red">Varesa</span> / <span style="color:red">Xilonen</span>|
|6.3  |<span style="color:green">Neuvillette</span> / <span style="color:red">Ineffa</span>|
|6.4  |<span style="color:red">Skirk</span> / <span style="color:red">Escoffier</span> / <span style="color:red">Flins</span>|
|6.5  |<span style="color:red">Chasca</span> / <span style="color:red">Lauma</span> / <span style="color:red">Nefer</span>|

Patch 5.0+
- Total Predicted: 41
- Correct Hits: 11
- Accuaracy: 26.83%

Patch 6.0+
- Total Predicted: 16
- Correct Hits: 3
- Accuracy: 18.75%

# Limitaions

While the model shows a significant lead over LWW (43.0% vs. 26.8&), The testing set is limited to 41 slots. A few lucky guesses or curveballs by hoyo could significantly alter these results. 

Testing will be continued in the future to see if these results continue. 

# Conclusions 

|Metric|Prediction Model             |LWW Heuristic|Improvement|
|------|-----------------------------|-------------|-----------|
|Total Accuracy (5.0+)|43.90%                       |26.83%       |+17.07%    |
|Recent Accuracy (6.0+)|50.00%                       |18.75%       |+31.25%    |


Overall, the prediction model performed better than the LWW heuristic. 

The obvious weakness that LWW has is characters who have debuted recently woudln't be guessed on their second or even third run. Characters with less total appearences tend to have less time in-between reruns, meaning they woudln't be guessed as they have less time off banner compared to older characters.

The model, however did capture some characters on their second and third reruns, showing that there is a rough pattern that can be learned. 

Also, there is bound to be unpredictable variables with predicting gacha game character reruns. Any reasons like popularity, meta relevance, events, and even quests could cause a character to run where the model would never predict them. 

# Version 6.6 Predictions

         Name  Predicted_prob  Predicted
        Durin            0.29          1
    Arlecchino           0.22          1