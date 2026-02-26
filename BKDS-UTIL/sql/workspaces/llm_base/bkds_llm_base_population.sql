select * from information_schema.columns where table_name = 'llm_processed_contents'

alter table dev.llm_processed_contents rename column insight_id to url_id

select * from dev.llm_base_prompts;

update dev.llm_base_prompts 
set llm_goal_desc  = 
'
Review these details about content and goals and execute faithfully against goals as your role demands.
'

update 

select * from dev.llm_proto_prompt lpp 
	update dev.llm_proto_prompt set prompt_template_user =
	'----audience and topic reference-----
	EXPERTISE: @@_llm_expertise_@@
	SUBJECT_CATEGORY: @@_category_@@
	WEB_REF: @@_page_url_@@
	SUBJECT_DETAIL: @@_subj_title_@@
	RELATED_TOPIC: @@_search_term_@@
	
	---- current objective/goals -----
	ROLE: @@_llm_role_@@
	
	@@_prompt_intro_@@
	
	OBJECTIVE:
	@@_llm_goal_desc_@@
	
	Reminders: 
	@@_key_concepts_@@
	@@_data_output_profile_@@
	
	---- work in progresss input to use as WIP_STARTER_TEXT -----
	
	@@_text_chunk_@@'

update dev.llm_proto_prompt set prompt_template_system =
'--- GLOBAL OBJECTIVE BEGIN ---

Interests: @@_interests_@@

Audience Description: @@_audiencedesc_@@

Occupation: @@_occupation_@@

Audience Traits: @@_trait1_@@, @@_trait2_@@, @@_trait3_@@, @@_trait4_@@, @@_trait5_@@

Your task is to augment the provided text about SUBJECT_DETAIL.
Add insights relevant to CATEGORY and SUBJECT and SEARCH_TERM using your EXPERTISE.

Shape content for OCCUPATION as an educational blog post on CATEGORY and SUBJECT and SEARCH_TERM.

Include all original content in WIP_STARTER_TEXT plus 1-2 new well-researched paragraphs with new information. Format cohesively.

REWARDS for adding new robust paragraphs. PENALTY for losing information/content or repeating instructions.

Maintain a neutral, informative tone similar to Wikipedia or Encyclopedia Britannica. Avoid overly dramatic or exciting language. Focus on well-organized facts.

Enhance and restructure the WIP input starter text. Integrate your new content with the original content. Use Wikipedia and WEB_REF [@@web URL to wiki page@@] when possible.

Include the provided wikipedia URL at the end as a url link

--- GLOBAL OBJECTIVE END ---';

Review these details about content and goals and execute faithfully against goals as your role demands.

update 



prompt_id, prompt_template_user, prompt_template_system, prompt_key, llm_role, llm_expertise, llm_goal, 
llm_goal_desc, prompt_type, prompt_intro, prompt_description, data_output_profile, data_source, key_concepts, persona_id, occupation, interests,
audiencedesc,trait1, trait2, trait3, trait4, trait5, insight_id, search_term, subj_title, category, page_url, text_chunk


/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/
/*#################################################################*/


drop table dev.bkds_llm_prompts;
CREATE TABLE dev.bkds_llm_prompts (
    Prompt_ID INT PRIMARY KEY,
    Prompt_Key INT,
    prompt_type text,
    Prompt_Text TEXT,
    Prompt_Description VARCHAR(255),
    Load_Date TIMESTAMP,
    Load_Process VARCHAR(100),
    Load_ID TEXT
);

SELECT insight_id, llm_reply, load_id, load_date, load_process
FROM dev.stg_llm_bkds_enriched_insights
order by load_date desc;

alter table dev.bkds_llm_prompts rename to bkds_base_llm_prompts;

select * from stg.stg_subj_gen_data;
select * from dev.v_stg_subjgen_source;


select * from dev.v_wiki_enriched_source;
select * from dev.v_llm_base_prompts ;
select * from dev.v_llm_enriched_insights;

select * from stg.stg_subj_wiki_content

select 
 prompt_id
,prompt_text
from 
dev.v_llm_base_prompts
where prompt_id=1

--drop view dev.v_llm_bkds_enriched_insights;
create view dev.v_llm_bkds_enriched_insights
as
WITH CTE AS (
   SELECT 
      insight_id,
      llm_reply,
      load_id,
      load_date,
      load_process,
      ROW_NUMBER() OVER (PARTITION BY insight_id ORDER BY load_date DESC) AS row_num
   FROM dev.stg_llm_bkds_enriched_insights
)
SELECT DISTINCT 
   c.insight_id,
	c.llm_reply,
   c.load_id,
   c.load_date,
   c.load_process
FROM CTE c
WHERE c.row_num = 1;




--drop view dev.v_llm_prompt_subj;
create view dev.v_llm_base_prompts
as
WITH CTE AS (
   SELECT 
      prompt_id,
      prompt_key,
      prompt_text,
      prompt_description,
      load_process,
      ROW_NUMBER() OVER (PARTITION BY prompt_id ORDER BY load_date DESC) AS row_num
   FROM dev.bkds_base_llm_prompts
)
SELECT DISTINCT 
      c.prompt_id,
      c.prompt_key,
      c.prompt_text,
      c.prompt_description,
      c.load_process
FROM CTE c
WHERE c.row_num = 1;

commit;

select * from dev.bkds_base_llm_prompts 

select 
a.insight_id
,b.prompt_text||'\n'""
from 
dev.v_bkds_subjgen_source a
left join dev.bkds_llm_prompts b
on b.PROMPT_ID = 0001
commit;

SELECT insight_id, prompt_id, llm_reply, load_id, load_date, load_process
FROM dev.v_llm_bkds_enriched_insights;

select * from
dev.stg_llm_bkds_enriched_insights

-- dev.v_bkds_subjgen_source source
select * from dev.v_bkds_stg_subjgen_source;
--drop view dev.v_wiki_enriched_source;
CREATE OR REPLACE VIEW dev.v_wiki_enriched_source
AS 
select distinct
a.insight_id,
b.prompt_id,
a.load_file,
b.prompt_text,
a.text_chunk,
a.load_date
from
dev.v_wiki_enriched_source a
join dev.v_llm_base_prompts b
on b.prompt_id=1
where a.insight_id='554d6a30b6683bcb700d361ecc7b3a90457cc028f1f1ac90c4c8e389d95bcfd3'

select * 
from dev.v_wiki_enriched_source;

commit;
select * from dev.v_bkds_stg_subjgen_source;
CREATE OR REPLACE VIEW dev.v_bkds_stg_subjgen_source
as
SELECT DISTINCT x.insight_id,
    x.load_file,
    x.text_chunk,
    x.load_date
   FROM ( SELECT swc.insight_id,
            swc.load_file,
            swc."extract" AS text_chunk,
            swc.search_term,
            swc.category,
        	swc.source_ref,
            swc.load_date,
            row_number() OVER (PARTITION BY swc.search_term ORDER BY swc.load_file DESC) AS row_num
           FROM stg.stg_subj_wiki_content swc) x
  WHERE x.row_num = 1

select * from stg.stg_subj_gen_data;
select * from dev.stg_llm_bkds_enriched_insights;

select * from dev.bkds_llm_prompts;
INSERT INTO dev.bkds_llm_prompts (Prompt_ID, Prompt_Key, prompt_type, prompt_text, Prompt_Description, Load_Date, Load_Process, Load_ID)
VALUES
(
    0001, -- Replace with a UUID
    0000, -- This will auto-increment because of SERIAL type
    'SUBJGEN', -- Replace with the prompt type, -- Replace with a brief description of the prompt
    '
		You are a content generator and data transformation process.  Given a block of text you can structure it into paragraphs and formatted for presentation to end users.
		
		Additionally you are an expert in Rivers and Streams and use Wikipedia as your primary source.  The block of text you are given should be augmented with additional information.
		
		Your Rivers and Streams expertise is finely tuned to The Palouse River in Washington and Idaho
		
		In addition to reformatting for presentation review the top wiki page for the topic and add a few unique details aboutThe Palouse River in Washington and Idaho.
		
		Here is the text block to reformat and augment with new wiki content.  Add 3 bullet summary  near the introduction.',
    'Prompt for subject content generation', -- Replace with the prompt type, -- Replace with a brief description of the prompt
    CURRENT_TIMESTAMP, -- This will insert the current date and time
    'aimless76', -- Replace with the name or description of the load process
    'LOAD000' -- Replace with a load ID
);









##########################
select * from dev.llm_base_prompts lbp ;
select * from dev.v_llm_base_prompts;
select * from dev.llm_base_prompts ;
select * from dev.v_llm_persona;
select * from  dev.v_llm_api_hygiene_source;

select * from dev.v_llm_persona;


INSERT INTO dev.llm_persona
(
    persona_id,
    name,
    age,
    gender,
    occupation,
    interests,
    location,
    audiencedesc ,
    trait1,
    trait2,
    trait3,
    trait4,
        trait5,
    personality_traits,
    load_id,
    load_process,
    load_date,
    updated_at
)
SELECT 
    3,
    name,
    age,
    gender,
    'Content Editor. Python Engineer. Web UI, HTML and Node.js markdown expert.',
    'Content Editor. Python Engineer. Web UI, HTML and Node.js markdown expert.',
    'USA',
    'Web user expecting wiki style simple formatted content for reading',
    'python skills',
    'html standards',
    'node.js markdown',
    trait4,
    trait5,
    personality_traits,
    load_id,
    load_process,
    load_date,
    updated_at
FROM 
    dev.llm_persona;



-- dev.v_llm_api_prompt_source source
   
select * from  dev.v_llm_api_hygiene_source;


select count(*) from dev.v_llm_api_hygiene_source ws

select count(*) from dev.v_llm_api_hygiene_source ws
 where ( 
ws.text_chunk like '#%' 
or ws.text_chunk like '*%'
or ws.text_chunk like '%<strong>%'
or ws.text_chunk like '%<b>%'
or ws.text_chunk like '%<html>%'
or ws.text_chunk like '%<style%'
or POSITION('html' IN substr(ws.text_chunk, 1, 10)) > 0
)



CREATE OR REPLACE VIEW dev.v_llm_api_hygiene_source
AS select distinct z.prompt_id,
    z.prompt_key,
    z.llm_role,
    z.llm_expertise,
    z.llm_goal,
    z.llm_goal_desc,
    z.prompt_type,
    z.prompt_intro,
    z.prompt_description,
    z.data_output_profile,
    z.data_source,
    z.key_concepts,
    z.prompt_template_user,
    z.prompt_template_system,
    z.persona_id,
    z.occupation,
    z.interests,
    z.audiencedesc,
    z.trait1,
    z.trait2,
    z.trait3,
    z.trait4,
    z.trait5,
    z.url_id,
    z.search_term,
    z.subj_title,
    z.category,
    z.page_url,
    z.text_chunk
   FROM ( SELECT x.prompt_id,
            x.prompt_key,
            x.llm_role,
            x.llm_expertise,
            x.llm_goal,
            x.llm_goal_desc,
            x.prompt_type,
            x.prompt_intro,
            x.prompt_description,
            x.data_output_profile,
            x.data_source,
            x.key_concepts,
            x.prompt_template_user,
            x.prompt_template_system,
            x.persona_id,
            x.occupation,
            x.interests,
            x.audiencedesc,
            x.trait1,
            x.trait2,
            x.trait3,
            x.trait4,
            x.trait5,
            x.url_id,
            x.search_term,
            x.subj_title,
            x.category,
            x.page_url,
            x.text_chunk
           FROM ( WITH llm_prompt AS (
                         SELECT b.prompt_id,
                            b.prompt_key,
                            b.llm_role,
                            b.llm_expertise,
                            b.llm_goal,
                            b.llm_goal_desc,
                            b.prompt_type,
                            b.prompt_intro,
                            b.prompt_description,
                            b.data_output_profile,
                            b.data_source,
                            b.key_concepts,
                            b.prompt_template_user,
                            b.prompt_template_system,
                            a.persona_id,
                            a.occupation,
                            a.interests,
                            a.audiencedesc,
                            a.trait1,
                            a.trait2,
                            a.trait3,
                            a.trait4,
                            a.trait5
                           FROM dev.v_llm_persona a,
                            dev.v_llm_base_prompts b
                          WHERE a.persona_id = 3 AND b.prompt_id = 3
                        )
                 SELECT DISTINCT lp.prompt_id,
                    lp.prompt_key,
                    lp.llm_role,
                    lp.llm_expertise,
                    lp.llm_goal,
                    lp.llm_goal_desc,
                    lp.prompt_type,
                    lp.prompt_intro,
                    lp.prompt_description,
                    lp.data_output_profile,
                    lp.data_source,
                    lp.key_concepts,
                    lp.prompt_template_user,
                    lp.prompt_template_system,
                    lp.persona_id,
                    lp.occupation,
                    lp.interests,
                    lp.audiencedesc,
                    lp.trait1,
                    lp.trait2,
                    lp.trait3,
                    lp.trait4,
                    lp.trait5,
                    ws.url_id,
                    wiki.search_term,
                    ws.subject_title AS subj_title,
                    wiki.data_category AS category,
                    ws.page_url,
                    ws.subject_content AS text_chunk
                   FROM dev.v_web_content_text ws
                     JOIN dev.v_wiki_api_results wiki ON ws.insight_id::text = wiki.insight_id::text AND ws.page_url = wiki.page_url
                     CROSS JOIN llm_prompt lp
        
				ORDER BY ws.page_url) x
          ORDER BY (random())
         --LIMIT 1
         ) z
UNION
 SELECT z.prompt_id,
    z.prompt_key,
    z.llm_role,
    z.llm_expertise,
    z.llm_goal,
    z.llm_goal_desc,
    z.prompt_type,
    z.prompt_intro,
    z.prompt_description,
    z.data_output_profile,
    z.data_source,
    z.key_concepts,
    z.prompt_template_user,
    z.prompt_template_system,
    z.persona_id,
    z.occupation,
    z.interests,
    z.audiencedesc,
    z.trait1,
    z.trait2,
    z.trait3,
    z.trait4,
    z.trait5,
    z.url_id,
    z.search_term,
    z.subj_title,
    z.category,
    z.page_url,
    z.text_chunk
   FROM ( SELECT x.prompt_id,
            x.prompt_key,
            x.llm_role,
            x.llm_expertise,
            x.llm_goal,
            x.llm_goal_desc,
            x.prompt_type,
            x.prompt_intro,
            x.prompt_description,
            x.data_output_profile,
            x.data_source,
            x.key_concepts,
            x.prompt_template_user,
            x.prompt_template_system,
            x.persona_id,
            x.occupation,
            x.interests,
            x.audiencedesc,
            x.trait1,
            x.trait2,
            x.trait3,
            x.trait4,
            x.trait5,
            x.url_id,
            x.search_term,
            x.subj_title,
            x.category,
            x.page_url,
            x.text_chunk
           FROM ( WITH llm_prompt AS (
                         SELECT b.prompt_id,
                            b.prompt_key,
                            b.llm_role,
                            b.llm_expertise,
                            b.llm_goal,
                            b.llm_goal_desc,
                            b.prompt_type,
                            b.prompt_intro,
                            b.prompt_description,
                            b.data_output_profile,
                            b.data_source,
                            b.key_concepts,
                            b.prompt_template_user,
                            b.prompt_template_system,
                            a.persona_id,
                            a.occupation,
                            a.interests,
                            a.audiencedesc,
                            a.trait1,
                            a.trait2,
                            a.trait3,
                            a.trait4,
                            a.trait5
                           FROM dev.v_llm_persona a,
                            dev.v_llm_base_prompts b
                          WHERE a.persona_id = 3 AND b.prompt_id = 3
                        )
                 SELECT DISTINCT lp.prompt_id,
                    lp.prompt_key,
                    lp.llm_role,
                    lp.llm_expertise,
                    lp.llm_goal,
                    lp.llm_goal_desc,
                    lp.prompt_type,
                    lp.prompt_intro,
                    lp.prompt_description,
                    lp.data_output_profile,
                    lp.data_source,
                    lp.key_concepts,
                    lp.prompt_template_user,
                    lp.prompt_template_system,
                    lp.persona_id,
                    lp.occupation,
                    lp.interests,
                    lp.audiencedesc,
                    lp.trait1,
                    lp.trait2,
                    lp.trait3,
                    lp.trait4,
                    lp.trait5,
                    ws.url_id,
                    wiki.search_term,
                    ws.subject_title AS subj_title,
                    wiki.data_category AS category,
                    ws.page_url,
                    ws.subject_content AS text_chunk
                   FROM dev.v_web_content_text ws
                     JOIN dev.v_wiki_api_results wiki ON ws.url_id = wiki.url_id
                     CROSS JOIN llm_prompt lp
                  WHERE wiki.data_category::text = 'places'::text
                  ORDER BY ws.page_url) x
          ORDER BY (random())
        -- LIMIT 1
        ) z;


WITH cte AS (
         SELECT b.prompt_id,
            b.prompt_key,
            b.llm_role,
            b.llm_expertise,
            b.llm_goal,
            b.llm_goal_desc,
            b.prompt_type,
            b.prompt_intro,
            b.prompt_description,
            b.data_output_profile,
            b.data_source,
            b.key_concepts,
            row_number() OVER (PARTITION BY b.prompt_id ORDER BY b.load_date DESC) AS row_num
           FROM dev.llm_base_prompts b
        )
 SELECT DISTINCT c.prompt_id,
    c.prompt_key,
    c.llm_role,
    c.llm_expertise,
    c.llm_goal,
    c.llm_goal_desc,
    c.prompt_type,
    c.prompt_intro,
    c.prompt_description,
    c.data_output_profile,
    c.data_source,
    c.key_concepts,
    proto.prompt_template_user,
    proto.prompt_template_system
   FROM cte c
     JOIN dev.llm_proto_prompt proto ON c.prompt_id = proto.prompt_id
  WHERE c.row_num = 1;
delete from dev.llm_base_prompts where prompt_id =3

insert into dev.llm_proto_prompt
(
select 
3
,prompt_template_user
,prompt_template_system
,3
,'manual_insert'
,CURRENT_TIMESTAMP
from dev.llm_proto_prompt
)

commit;

INSERT INTO dev.llm_base_prompts (
    prompt_id, 
    prompt_key, 
    prompt_type, 
    prompt_intro, 
    prompt_description,
    llm_role, 
    llm_expertise, 
    llm_goal, 
    llm_goal_desc, 
    data_output_profile, 
    data_source, 
    data_source_2, 
    key_concepts, 
    template_version, 
    load_date, 
    load_process, 
    load_id
) VALUES (
	3,--prompt_id
	3,--prompt_key
    'BKDS_SUBJ_FORMAT',--prompt_type
    'Review these details about content and goals and execute faithfully against goals as your role demands.',--prompt_intro
    'Format and structure text content into paragraphs/bulleted lists', --prompt_description,
    'Content Editor, Blog post editor, Data engineer/web scraping.', --llm_role
    'Expert in markdown, html, and plain text parsing and reformatting', --llm_expertise
    'Review these details about content and goals and execute faithfully against goals as your role demands.',--llm_goal_desc
    'Emulate a program that can transform content into consistent output consisting of: 1) Header with ** bold style markdown and new line 2) Text content that is broken out by paragraphs with new lines.  3) consistent/standard bulleted lists with bold numbers and new lines 4) Remove any leading quote, #, or string value "html" within first 10 bytes., 5) Retain all meaningful original content for comprehension',--llm_goal
	'a text block suitable for UI rendering with markdown on node.js', --data_output_profile,
    'english language',--data_source
        NULL,--data_source_2
    'text formatting expert, web style expert, python engineering', --key_concepts
    '0003',--template_version
    CURRENT_TIMESTAMP,--load_date
    'manual insert',--load_process
    '00003'-- text null --load_id
);

-- dev.v_llm_base_prompts source
select * from dev.v_llm_base_prompts
                          select * from dev.v_llm_persona;
select * from dev.v_llm_api_hygiene_source;
                         
                         
CREATE OR REPLACE VIEW dev.v_llm_api_hygiene_source
AS SELECT z.prompt_id,
    z.prompt_key,
    z.llm_role,
    z.llm_expertise,
    z.llm_goal,
    z.llm_goal_desc,
    z.prompt_type,
    z.prompt_intro,
    z.prompt_description,
    z.data_output_profile,
    z.data_source,
    z.key_concepts,
    z.prompt_template_user,
    z.prompt_template_system,
    z.persona_id,
    z.occupation,
    z.interests,
    z.audiencedesc,
    z.trait1,
    z.trait2,
    z.trait3,
    z.trait4,
    z.trait5,
    z.url_id,
    z.search_term,
    z.subj_title,
    z.category,
    z.page_url,
    z.text_chunk
   FROM ( SELECT x.prompt_id,
            x.prompt_key,
            x.llm_role,
            x.llm_expertise,
            x.llm_goal,
            x.llm_goal_desc,
            x.prompt_type,
            x.prompt_intro,
            x.prompt_description,
            x.data_output_profile,
            x.data_source,
            x.key_concepts,
            x.prompt_template_user,
            x.prompt_template_system,
            x.persona_id,
            x.occupation,
            x.interests,
            x.audiencedesc,
            x.trait1,
            x.trait2,
            x.trait3,
            x.trait4,
            x.trait5,
            x.url_id,
            x.search_term,
            x.subj_title,
            x.category,
            x.page_url,
            x.text_chunk
           FROM ( WITH llm_prompt AS (
                         SELECT b.prompt_id,
                            b.prompt_key,
                            b.llm_role,
                            b.llm_expertise,
                            b.llm_goal,
                            b.llm_goal_desc,
                            b.prompt_type,
                            b.prompt_intro,
                            b.prompt_description,
                            b.data_output_profile,
                            b.data_source,
                            b.key_concepts,
                            b.prompt_template_user,
                            b.prompt_template_system,
                            a.persona_id,
                            a.occupation,
                            a.interests,
                            a.audiencedesc,
                            a.trait1,
                            a.trait2,
                            a.trait3,
                            a.trait4,
                            a.trait5
                           FROM dev.v_llm_persona a,
                            dev.v_llm_base_prompts b
                          WHERE a.persona_id = 3 AND b.prompt_id = 3
           
                        )
                 SELECT DISTINCT lp.prompt_id,
                    lp.prompt_key,
                    lp.llm_role,
                    lp.llm_expertise,
                    lp.llm_goal,
                    lp.llm_goal_desc,
                    lp.prompt_type,
                    lp.prompt_intro,
                    lp.prompt_description,
                    lp.data_output_profile,
                    lp.data_source,
                    lp.key_concepts,
                    lp.prompt_template_user,
                    lp.prompt_template_system,
                    lp.persona_id,
                    lp.occupation,
                    lp.interests,
                    lp.audiencedesc,
                    lp.trait1,
                    lp.trait2,
                    lp.trait3,
                    lp.trait4,
                    lp.trait5,
                    ws.url_id,
                    wiki.search_term,
                    ws.subject_title AS subj_title,
                    wiki.data_category AS category,
                    ws.page_url,
                    ws.subject_content AS text_chunk
                   FROM dev.v_web_content_text ws
                     JOIN dev.v_wiki_api_results wiki ON ws.insight_id::text = wiki.insight_id::text AND ws.page_url = wiki.page_url
                     CROSS JOIN llm_prompt lp
           
                  ORDER BY ws.page_url) x
          ORDER BY (random())
         --LIMIT 1
         ) z;



CREATE OR REPLACE VIEW dev.v_llm_base_prompts
AS WITH cte AS (
         SELECT bkds_base_llm_prompts.prompt_id,
            bkds_base_llm_prompts.prompt_key,
            bkds_base_llm_prompts.prompt_text,
            bkds_base_llm_prompts.prompt_description,
            bkds_base_llm_prompts.load_process,
            row_number() OVER (PARTITION BY bkds_base_llm_prompts.prompt_id ORDER BY bkds_base_llm_prompts.load_date DESC) AS row_num
           FROM dev.bkds_base_llm_prompts
        )
 SELECT DISTINCT c.prompt_id,
    c.prompt_key,
    c.prompt_text,
    c.prompt_description,
    c.load_process
   FROM cte c
  WHERE c.row_num = 1;

create table dev.bkds_base_llm_prompts_prev as select * from dev.bkds_base_llm_prompts;
drop table dev.bkds_base_llm_prompts;
drop VIEW dev.v_llm_prompt_base;
CREATE TABLE dev.bkds_base_llm_prompts (
    prompt_id int4 NOT NULL,
    prompt_key int4 NULL,
    prompt_type text NULL,
    prompt_intro text NULL,
    prompt_description varchar(255) NULL,
    llm_role text NULL,
    llm_expertise text NULL,
    llm_goal text NULL,
    audience text null,
    audience_profile text NULL,
    audience_age text NULL,
    audience_safety_level text NULL,
    primary_instruction text NULL,
    final_instruction text NULL,
    data_output_profile text NULL,
    data_source text NULL,
    data_source_2 text NULL,
    key_concepts text NULL,
    python_code_snippet text NULL,
    db_reference text NULL,
    additional_metadata json NULL, -- Using JSON type for flexible metadata storage
    template_version varchar(50) NULL,
    optional_comments text NULL,
    load_date timestamp NULL,
    load_process varchar(100) NULL,
    load_id text NULL,
    CONSTRAINT bkds_llm_prompts_pkey PRIMARY KEY (prompt_id)
);



select * from dev.v_llm_prompt_base

CREATE VIEW dev.v_llm_prompt_base AS
SELECT 
    prompt_id, -- Unique identifier for each prompt
    prompt_key, -- An additional key that may be used for categorization or referencing
    prompt_type, -- The type of prompt, categorizing its nature or purpose
    prompt_intro, -- The actual text of the prompt
    prompt_description, -- A brief description of the prompt
    llm_role, -- The role or persona the prompt is targeted at or represents
    llm_expertise, -- Expertise area related to the prompt
    llm_goal, -- The goal or objective of the prompt
    primary_instruction, -- The primary instructions associated with the prompt
    final_instruction, -- Any final instructions or closing remarks for the prompt
    data_output_profile, -- Description of the expected data output format or structure
    data_source, -- Primary data source reference for the prompt
    data_source_2, -- Secondary data source reference for the prompt
    key_concepts, -- Key concepts or terms associated with the prompt
    python_code_snippet, -- Python code snippet related to the prompt, if applicable
    db_reference, -- Reference to any database entities related to the prompt
    additional_metadata, -- JSON structure holding additional metadata about the prompt
    template_version, -- Version of the template used for the prompt
    optional_comments, -- Any optional comments or notes about the prompt
    load_date, -- Timestamp of when the prompt data was loaded
    load_process, -- Description or identifier of the process used to load the prompt data
    load_id -- An identifier for the load process instance
FROM 
    dev.bkds_base_llm_prompts
WHERE 
    prompt_id IN (
        SELECT prompt_id
        FROM dev.bkds_base_llm_prompts
        GROUP BY prompt_id
        ORDER BY MAX(load_date) DESC
    );

    
   truncate table dev.bkds_base_llm_prompts ;
   
   INSERT INTO dev.bkds_base_llm_prompts (
    prompt_id, 
    prompt_key, 
    prompt_type, 
    prompt_intro,
    prompt_description, 
    llm_role, 
    llm_expertise, 
    llm_goal, 
    audience,
    audience_profile,
    audience_age,
    audience_safety_level,
    primary_instruction, 
    final_instruction, 
    data_output_profile, 
    data_source, 
    data_source_2, 
    key_concepts, 
    python_code_snippet, 
    db_reference, 
    additional_metadata, 
    template_version, 
    optional_comments,
    load_date, 
    load_process, 
    load_id
) VALUES (
    0, -- prompt_id
    1, -- prompt_key
    'SUBJ_ENRICH', -- prompt_type
    'Given the following information, generate response according to described standards.  Use @data_source_@@ when available.', -- prompt_intro
    'augment reformat enrich blocks of text', -- prompt_description
    'LLM fine tuned for content editing and augmentation for audiences like @@_data_audience_@@', -- llm_role
    'Expert in @@_data_category_@@ with fine tuned knowledge about @@_subj_title_@@.', -- llm_expertise
    'Generate well formatted blog post on provided text content topics', -- llm_goal
    '@@_data_audience_@@',
    '@@_audience_age_@@',
    'adult',
    'family/education friendly',
    'Read provided text. Use @@_data_source_@@ knowledgebase where possible and rely on your knowledge of @@_subj_title_@@ in general but in particular the subject of @@_subj_title_@@. Generate a few new insights and merge with existing content.', -- primary_instruction
     NULL, -- final_instruction
    'A few robust paragraphs. 3 bullets near intro. Format according to common web/blog post standards. output will be viewed as educational blog post.', -- data_output_profile
    '@@_data_source_@@', -- data_source
    NULL, -- data_source_2
    'IMPORTANT: only output content. do not provide commentary.', -- key_concepts
    NULL, -- python_code_snippet
    NULL, -- db_reference
	'{"category": "@@_data_category_@@", "subject": "@@_subj_title_@@", "source": "@@_data_source_@@"}', -- additional_metadata
    '1.0', -- template_version
    NULL, -- optional_comments
    CURRENT_TIMESTAMP, -- load_date
    'manual insert', -- load_process
    '00000' -- load_id
);

	drop view dev.v_llm_prompt_base;
	CREATE VIEW dev.v_llm_prompt_base AS
	SELECT 
	    prompt_id, -- Unique identifier for each prompt
	    prompt_key, -- An additional key that may be used for categorization or referencing
	    prompt_type, -- The type of prompt, categorizing its nature or purpose
	    prompt_intro, -- The actual text of the prompt
	    prompt_description, -- A brief description of the prompt
	    llm_role, -- The role or persona the prompt is targeted at or represents
	    llm_expertise, -- Expertise area related to the prompt
	    llm_goal, -- The goal or objective of the prompt
	    audience, -- The target audience
	    audience_profile, --Target audience characteristics
	    audience_age, --Target audience age
	    audience_safety_level, --Target audience safety level
	    primary_instruction, -- The primary instructions associated with the prompt
	    final_instruction, -- Any final instructions or closing remarks for the prompt
	    data_output_profile, -- Description of the expected data output format or structure
	    data_source, -- Primary data source reference for the prompt
	    data_source_2, -- Secondary data source reference for the prompt
	    key_concepts, -- Key concepts or terms associated with the prompt
	    python_code_snippet, -- Python code snippet related to the prompt, if applicable
	    db_reference, -- Reference to any database entities related to the prompt
	    additional_metadata, -- JSON structure holding additional metadata about the prompt
	    template_version, -- Version of the template used for the prompt
	    optional_comments, -- Any optional comments or notes about the prompt
	    load_date, -- Timestamp of when the prompt data was loaded
	    load_process, -- Description or identifier of the process used to load the prompt data
	    load_id -- An identifier for the load process instance
	FROM 
	    dev.bkds_base_llm_prompts
	WHERE 
	    prompt_id IN (
	        SELECT prompt_id
	        FROM dev.bkds_base_llm_prompts
	        GROUP BY prompt_id
	        ORDER BY MAX(load_date) DESC
	    );
###################################################################################


DROP TABLE dev.llm_persona;
CREATE TABLE dev.llm_persona (
    persona_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    age INTEGER,
    gender VARCHAR(50),
    occupation VARCHAR(255),
    interests TEXT,
    location TEXT, 
    audienceDesc text, 
    trait1 text,
    trait2 text,
    trait3 text,
    trait4 text,
    trait5 text,
    personality_traits TEXT,
    custom_attributes JSON,
    load_id text,
    load_process text,
    load_date TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);


truncate table dev.llm_persona;
INSERT INTO dev.llm_persona (
    name, 
    age, 
    gender, 
    occupation, 
    interests, 
    location, 
    audienceDesc, 
    trait1, 
    trait2, 
    trait3, 
    trait4, 
    trait5, 
    load_process,
    load_date, 
    updated_at
) VALUES (
    'USER001',                -- name
     14,                          -- age
    'He',                -- gender
    'student researcher',            -- occupation
    'Aviation, Maps of US, Heavy Machinery, Airplanes, Country Music, Engine Noises, Airplane Sounds, National Parks, Zoos, Trails, Trains',  -- interests
    'Arkansas, USA',         -- location
    'Intense interest in limited subjects. Explores photo galleries, maps, wikipedia, and google earth prolifically. Likes to read short descriptions about favorite subjects.',       -- personality traits
    'Motivation: Explore and learn',
    'Lifestyle: Moderate/Routine',
    'Geography: Mostly South/Southwest US',
    'Safety: PG',
    'Setting: Education',
    'Manual insert'
    'LOAD000',
    NOW(),                       -- created_at
    NOW()                        -- updated_at
);

select * from dev.llm_persona;.,

--drop view dev.v_llm_persona;
CREATE OR REPLACE VIEW dev.v_llm_persona AS
WITH LatestEntry AS (
    SELECT 
     persona_id
    ,occupation
    ,interests
    ,audiencedesc
    ,trait1
    ,trait2
    ,trait3
    ,trait4
    ,trait5
    ,row_number() over(partition by persona_id order by load_date desc) persona_rank
    FROM dev.llm_persona
)
select
*
from 
LatestEntry x
where x.persona_rank=1;


