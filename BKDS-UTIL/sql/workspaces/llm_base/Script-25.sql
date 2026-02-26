select * from 
dev.v_llm_api_prompt_source

select 
count(*)
,count(distinct url_id)
from dev.v_web_content_text


select *
from dev.v_web_content_text

SELECT 
    substr(subject_content, 1, 3) AS prefix,
    COUNT(*)
FROM 
    dev.v_web_content_text
WHERE 
    POSITION('html' IN substr(subject_content, 1, 10)) > 0
GROUP BY 
    substr(subject_content, 1, 3);

   select subject_content
   FROM 
    dev.v_web_content_text
WHERE 
    POSITION('html' IN substr(subject_content, 1, 10)) > 0


select 
substr(subject_content, 0, 5)
,count(*)
from dev.v_web_content_text
where subject_content like '#%' 
or subject_content like '*%'
or subject_content like '%<strong>%'
or subject_content like '%<b>%'
or subject_content like '%<html>%'
or subject_content like '%<style%'
or POSITION('html' IN substr(subject_content, 1, 10)) > 0
group by substr(subject_content, 0, 5);



select count(*) from dev.v_llm_enriched_insights
select count(*) from dev.llm_processed_contents
select * from dev.llm_base_prompts lbp 

Expert on @@_search_term_@@ in the @@_category_@@ and @@_subj_title_@@ domain.

--base prompt: has prompt intro, descriptoin, expertise, and values to be replaced in proto prompt like goal, output profile, etc
-- proto prompt: has prompt template for user and prompt template for the dynamic substitution

-- FOR TEXT CONTENT HYGIENE --
-- you need new base prompt that will re-use proto prompt. 
-- a view for hygiene source similar to prompt gen source
-- a new SQL query template for hygiene source query

-- llm_processed_contents: API chat results

select * from 
dev.llm_persona
select * from dev.llm_proto_prompt




select * from dev.llm_processed_contents

select * from dev.v_llm_base_prompts vlbp 

select count(*) from
(
select url_id, count(*)
from dev.llm_processed_contents
group by url_id 
having count(url_id) > 1
) x;


