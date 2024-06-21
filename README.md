
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip freeze > requirements.txt
pip install -r requirements.txt
flask run
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt


-- CREATE TABLE nex_score (
--     market VARCHAR(100),
--     Region VARCHAR(100),
--     Detractor_Count INT,
--     Neutral_Count INT,
--     Influencer_Count INT,
--     total INT,
--     Detractor_perc DECIMAL(5,2),
--     Neutral_perc DECIMAL(5,2),
--     Influencer_perc DECIMAL(5,2),
--     Update_Date DATE
-- );

-- ALTER TABLE nex_score ADD COLUMN id SERIAL PRIMARY KEY;

### python -m unittest discover -s tests -v
### python -m unittest test_file_name.py





-- CREATE TABLE nex_score_temp (
--     market VARCHAR(100),
--     Region VARCHAR(100),
--     Detractor_Count INT,
--     Neutral_Count INT,
--     Influencer_Count INT,
--     total INT,
--     Detractor_perc DECIMAL(5, 2),
--     Neutral_perc DECIMAL(5, 2),
--     Influencer_perc DECIMAL(5, 2),
--     Update_Date_Str VARCHAR(10)  -- Date as string in MM/DD/YYYY format
-- );
-- CREATE TABLE nex_score (
--     market VARCHAR(100),
--     Region VARCHAR(100),
--     Detractor_Count INT,
--     Neutral_Count INT,
--     Influencer_Count INT,
--     total INT,
--     Detractor_perc DECIMAL(5, 2),
--     Neutral_perc DECIMAL(5, 2),
--     Influencer_perc DECIMAL(5, 2),
--     Update_Date DATE
-- );

INSERT INTO nex_score (market, Region, Detractor_Count, Neutral_Count, Influencer_Count, total, Detractor_perc, Neutral_perc, Influencer_perc, Update_Date)
SELECT 
    market, 
    Region, 
    Detractor_Count, 
    Neutral_Count, 
    Influencer_Count, 
    total, 
    Detractor_perc, 
    Neutral_perc, 
    Influencer_perc,
    STR_TO_DATE(Update_Date_Str, '%m/%d/%Y') AS Update_Date
FROM nex_score_temp;

