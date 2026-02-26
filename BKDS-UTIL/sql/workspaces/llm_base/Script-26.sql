
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
select * from dev.llm_proto_prompt;

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

select * from dev.llm_proto_prompt 
update dev.llm_proto_prompt set prompt_template_system =
'--- GLOBAL OBJECTIVE BEGIN ---
Interests: @@_interests_@@
Audience Description: @@_audiencedesc_@@
ABOUT YOU: @@_occupation_@@
Audience Traits: @@_trait1_@@, @@_trait2_@@, @@_trait3_@@, @@_trait4_@@, @@_trait5_@@

Your task is to FORMAT AND STRUCTURE the provided text about SUBJECT_DETAIL.

Use your EXPERTISE related to GOAL of handling diverse marked up/down HTML or plaintext content and wrangling it into a common layout for all CONTENT

Shape content for OCCUPATION as an educational blog post on CATEGORY and SUBJECT and SEARCH_TERM OR CONTENT. Format cohesively.

PENALTY for losing information/content or repeating instructions.
--- GLOBAL OBJECTIVE END --'
where prompt_id=3;


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

 WITH cte AS (
         SELECT vlei.url_id AS insight_id,
            vlei.content AS llm_reply,
            vlei.load_id,
            vlei.load_date,
            vlei.load_process,
            vlei.page_url,
            md5((vlei.page_url)::text) AS url_id,
            row_number() OVER (PARTITION BY (md5((vlei.page_url)::text)) ORDER BY vlei.load_date DESC) AS row_num
           FROM llm_processed_contents vlei
        )
 SELECT DISTINCT c.insight_id,
    c.llm_reply,
    c.load_id,
    c.load_date,
    c.url_id,
    c.page_url,
    c.load_process
   FROM cte c
  WHERE (c.row_num = 1);

create table dev.stg_llm_processed_contents as select * from dev.llm_processed_contents where 0=1;
select * from dev.v_llm_api_hygiene_source
select * from dev.bkds_enriched_insights;
select * from dev.llm_processed_contents lpc ;

select 
count(*)
,count(distinct a.url_id)

select a.*
,lpc.*
from dev.v_llm_api_hygiene_source a
left join dev.llm_processed_contents lpc 
on a.page_url = lpc.page_url
where lpc.prompt_id is not null;


select * from information_schema.views where view_definition like '%llm_processed_contents%'

select count(*) 
from dev.v_llm_api_hygiene_source
--1682
where url_id = '005018a8cab1548138200ade071b86b9'

select count(*) from wh.v_web_content_feed_master

where ( default_img not like '%jpeg%' and  default_img not like
'%JPEG%')

-- wh.v_web_content_feed_master source

CREATE OR REPLACE VIEW wh.v_web_content_feed_master
AS SELECT DISTINCT tbl_web_feed_master.cluster_id,
    tbl_web_feed_master.url_id,
    tbl_web_feed_master.subject_id,
    tbl_web_feed_master.subject_title,
    tbl_web_feed_master.default_img,
    tbl_web_feed_master.data_category,
    tbl_web_feed_master.data_category_id,
    tbl_web_feed_master.data_subject,
    tbl_web_feed_master.data_subject_id,
    tbl_web_feed_master.images,
    tbl_web_feed_master.videos,
    tbl_web_feed_master.featured_images,
    tbl_web_feed_master.related_topics,
    tbl_web_feed_master.subject_content,
    tbl_web_feed_master.data_category AS content_name
   FROM wh.tbl_web_feed_master
  where ( lower(default_img) not like '%.jpeg%');

select COUNT(*), COUNT(distinct URL_ID) from dev.stg_llm_processed_contents
where content like '**%'

select SUBSTR(replace(content, ' ', ''), 0, 5), 
COUNT(*), COUNT(distinct URL_ID) from dev.stg_llm_processed_contents
where content like '#%'
and SUBSTR(replace(content, ' ', ''), 0, 5) not like '# **'
group by SUBSTR(replace(content, ' ', ''), 0, 5)

create table dev.stg_llm_processed_contents_bkup as select * from dev.stg_llm_processed_contents;
insert into dev.stg_llm_processed_contents (select * from dev.stg_llm_processed_contents_bkup);
select * from dev.v_llm_api_prompt_source

-- dev.v_llm_enriched_insights source
select count(*), count(distinct page_url) from dev.v_llm_hygiene_results;
CREATE OR REPLACE VIEW dev.v_llm_hygiene_results
AS WITH cte AS (
         SELECT vlei.url_id AS insight_id,
            vlei.content AS llm_reply,
            vlei.load_id,
            vlei.load_date,
            vlei.load_process,
            vlei.page_url,
            md5(vlei.page_url::text) AS url_id,
            row_number() OVER (PARTITION BY (md5(vlei.page_url::text)) ORDER BY vlei.load_date DESC) AS row_num
           FROM dev.stg_llm_processed_contents vlei
        )
 SELECT DISTINCT c.insight_id,
    c.llm_reply,
    c.load_id,
    c.load_date,
    c.url_id,
    c.page_url,
    c.load_process
   FROM cte c
  WHERE c.row_num = 1;
 
 
UPDATE dev.stg_llm_processed_contents
SET content = CASE
    WHEN content LIKE '####%' THEN SUBSTRING(content FROM 5)
    WHEN content LIKE '###%' THEN SUBSTRING(content FROM 4)
    WHEN content LIKE '##%' THEN SUBSTRING(content FROM 3)
    WHEN content LIKE '#%' THEN SUBSTRING(content FROM 2)
    ELSE content
END
WHERE content LIKE '#%';

v_llm_api_prompt_source

create table 
dev.stg_llm_processed_subjgen_contents_11162024
as 
select distinct  * from dev.stg_llm_processed_subjgen_contents slpsc;

truncate table  dev.stg_llm_processed_subjgen_contents;

select count(*), count(distinct url_id)
from  dev.v_wiki_api_results 
where data_category like '%places%'

v_web_content_img
v_subject_master_index
v_web_content_text

 wh.tbl_web_content_img_master
 
select count(*) ,count(distinct url_id)
from wh.tbl_subject_master_index
 
create table wh.tbl_subject_master_index as select distinct * from dev.v_subject_master_index;

create table wh.llm_processed_contents as select distinct * from dev.llm_processed_contents;
select * from dev.stg_llm_processed_subjgen_contents slpsc 
select * from dev.stg_llm
select * from  wh.llm_processed_contents;

select 
count(*) 
,count(distinct url_id)
from wh.tbl_web_content_feed_master twcfm 
where substr(replace(ltrim(rtrim(subject_content)), ' ', ''), 0, 50) like '**%'


select count(*), count(distinct url_id)
from wh.tbl_web_subject_content_master twscm 

select count(*), count(distinct url_id)
from wh.v_web_content_feed__master

select count(*), count(distinct cluster_id)
from wh.v_web_content_media_cluster


select * from  wh.tbl_web_content_media_cluster ;


SELECT DISTINCT v_index.cluster_id,
    v_index.url_id,
    v_index.subject_id,
    cat.data_category,
    cat.data_subject,
    md5(cat.data_category::text) AS data_category_id,
    md5(cat.data_subject) AS data_subject_id,
    v_index.subject_title,
    v_index.page_url,
    img_url as default_img,
    media.images,
    feat.images AS featured_images,
    media.videos,
    related.related_topics,
    txt.subject_content
   FROM wh.tbl_subject_master_index v_index
     JOIN wh.tbl_web_content_feed_master txt ON txt.url_id = v_index.url_id::text
     JOIN wh.tbl_web_content_media_cluster media ON v_index.cluster_id::text = media.cluster_id::text
     JOIN wh.tbl_content_media_url feat ON v_index.url_id::text = feat.url_id::text
     JOIN wh.tbl_web_content_categories cat ON v_index.url_id::text = cat.url_id::text
     JOIN dev.v_web_content_related_topics related ON v_index.url_id::text = related.url_id::text
     join dev.v_default_img_ref def_img on v_index.url_id = def_img.url_id


     
create table wh.tbl_content_media_url
as select * from wh.v_content_media_url


CREATE OR REPLACE VIEW wh.v_content_media_url
AS SELECT tsmi.url_id,
    COALESCE(jsonb_agg(DISTINCT img.json_object) FILTER (WHERE (img.json_object IS NOT NULL)), '[]'::jsonb) AS images,
    COALESCE(jsonb_agg(DISTINCT vid.json_object) FILTER (WHERE (vid.json_object IS NOT NULL)), '[]'::jsonb) AS videos
   FROM (((dev.v_subject_master_index tsmi
     JOIN dev.v_web_content_text txt ON (((txt.subject_id = (tsmi.subject_id)::text) AND ((txt.search_id)::text = (tsmi.search_id)::text) AND (txt.url_id = (tsmi.url_id)::text))))
     LEFT JOIN LATERAL ( SELECT img_data.search_id,
            jsonb_build_object('img_url_id', img_data.img_url_id, 'img_url', img_data.img_url, 'img_src', img_data.data_source, 'img_title', img_data.img_title) AS json_object
           FROM wh.tbl_web_content_img_master  img_data
          WHERE ((img_data.data_source IS NOT NULL) AND (img_data.img_url_id IS NOT NULL))
          GROUP BY img_data.search_id, img_data.img_url_id, img_data.img_url, img_data.data_source, img_data.img_title) img ON (((img.search_id)::text = (tsmi.search_id)::text)))
     LEFT JOIN LATERAL ( SELECT vid_data.search_id,
            jsonb_build_object('vid_url_id', vid_data.vid_url_id, 'vid_thumb_id', vid_data.vid_thumb_id, 'vid_thumb_url', vid_data.vid_thumb, 'vid_title', vid_data.vid_title, 'vid_url', vid_data.vid_url) AS json_object
           FROM wh.tbl_web_content_video_master vid_data
          WHERE ((vid_data.vid_url_id IS NOT NULL) AND (vid_data.vid_title IS NOT NULL))
          GROUP BY vid_data.search_id, vid_data.vid_url_id, vid_data.vid_thumb_id, vid_data.vid_thumb, vid_data.vid_title, vid_data.vid_url) vid ON (((vid.search_id)::text = (tsmi.search_id)::text)))
  GROUP BY tsmi.url_id;
 
 
create table wh.tbl_web_content_media_cluster 
as
select distinct * from wh.v_web_content_media_cluster;
select * from wh.tbl_web_content_categories
create or replace view wh.v_web_content_media_cluster
as
 SELECT tsmi.cluster_id,
    COALESCE(jsonb_agg(DISTINCT img.json_object) FILTER (WHERE (img.json_object IS NOT NULL)), '[]'::jsonb) AS images,
    COALESCE(jsonb_agg(DISTINCT vid.json_object) FILTER (WHERE (vid.json_object IS NOT NULL)), '[]'::jsonb) AS videos
   FROM (((wh.tbl_subject_master_index tsmi
     JOIN wh.tbl_web_subject_content_master txt ON (((txt.subject_id = (tsmi.subject_id)::text) AND ((txt.search_id)::text = (tsmi.search_id)::text) AND (txt.url_id = (tsmi.url_id)::text))))
     LEFT JOIN LATERAL ( SELECT img_data.search_id,
            jsonb_build_object('img_url_id', img_data.img_url_id, 'img_url', img_data.img_url, 'img_src', img_data.data_source, 'img_title', img_data.img_title) AS json_object
           FROM wh.tbl_web_content_img_master  img_data
          WHERE ((img_data.data_source IS NOT NULL) AND (img_data.img_url_id IS NOT NULL))
          GROUP BY img_data.search_id, img_data.img_url_id, img_data.img_url, img_data.data_source, img_data.img_title) img ON (((img.search_id)::text = (tsmi.search_id)::text)))
     LEFT JOIN LATERAL ( SELECT vid_data.search_id,
            jsonb_build_object('vid_url_id', vid_data.vid_url_id, 'vid_thumb_id', vid_data.vid_thumb_id, 'vid_thumb_url', vid_data.vid_thumb, 'vid_title', vid_data.vid_title, 'vid_url', vid_data.vid_url) AS json_object
           FROM wh.tbl_web_content_video_master vid_data
          WHERE ((vid_data.vid_url_id IS NOT NULL) AND (vid_data.vid_title IS NOT NULL))
          GROUP BY vid_data.search_id, vid_data.vid_url_id, vid_data.vid_thumb_id, vid_data.vid_thumb, vid_data.vid_title, vid_data.vid_url) vid ON (((vid.search_id)::text = (tsmi.search_id)::text)))
  GROUP BY tsmi.cluster_id;
 
 
select default_img , images from wh.v_web_content_feed_master vwcfm 

select * from wh.tbl_web_content_img_master twcim 
where img_url like '%jason%'

create or replace view wh.v_web_content_feed_master
as
  SELECT DISTINCT a.cluster_id,
    a.url_id,
    a.subject_id,
    a.subject_title,
    a.default_img,
    a.data_category,
    a.data_category_id,
    a.data_subject,
    a.data_subject_id,
    a.images,
    a.videos,
    a.featured_images,
    a.related_topics,
    COALESCE(b.subject_content, a.subject_content) AS subject_content,
    a.data_category AS content_name
   FROM (wh.tbl_web_feed_master a
     LEFT JOIN wh.tbl_web_subject_content_master b ON (((a.url_id)::text = b.url_id)))
  WHERE (lower(a.default_img) !~~ '%.jpeg%'::text);

select 
a.*
from wh.tbl_web_subject_content_master_new a
join (
select * from 
(
select url_id, count(*)
from wh.tbl_web_subject_content_master
group by url_id
having count(url_id) > 1) x
) z
on a.url_id = z.url_id
order by a.url_id desc;

create table bkup.tbl_web_subject_content_master_11172024
as select * from wh.tbl_web_subject_content_master

drop table  wh.tbl_web_subject_content_master cascade
alter table wh.tbl_web_subject_content_master_new rename to tbl_web_subject_content_master
create table wh.tbl_web_subject_content_master_new
as
WITH llm_ranked AS (
  SELECT
    url_id,
    llm_reply,
    ROW_NUMBER() OVER (PARTITION BY url_id ORDER BY load_date DESC) AS rnk
  FROM wh.v_llm_subject_content
),
deduplicated_llm AS (
  SELECT 
    url_id, 
    llm_reply
  FROM llm_ranked
  WHERE rnk = 1
)
SELECT DISTINCT
  subj.subject_id,
  subj.insight_id,
  subj.search_id,
  subj.page_url,
  subj.search_term,
  subj.subject_title,
  subj.url_id,
  COALESCE(deduplicated_llm.llm_reply, subj.subject_content) AS subject_content,
  CASE 
    WHEN deduplicated_llm.llm_reply IS NOT NULL THEN 'LLM' 
    ELSE 'WH' 
  END AS SUBJ_SOURCE,
  subj.data_source
FROM wh.tbl_web_subject_content_master subj
LEFT JOIN deduplicated_llm
  ON subj.url_id = deduplicated_llm.url_id;

 
select * from  wh.v_llm_subject_content ;
;
select * from wh.tbl_web_subject_content_master;
select * from wh.v_llm_subject_content;
create view wh.v_llm_subject_content
as
 WITH cte AS (
         SELECT vlei.url_id AS insight_id,
            vlei.content AS llm_reply,
            vlei.load_id,
            vlei.load_date,
            vlei.load_process,
            vlei.page_url,
            md5((vlei.page_url)::text) AS url_id,
            row_number() OVER (PARTITION BY (md5((vlei.page_url)::text)) ORDER BY vlei.load_date DESC) AS row_num
           FROM wh.llm_processed_contents vlei
        )
 SELECT DISTINCT c.insight_id,
    c.llm_reply,
    c.load_id,
    c.load_date,
    c.url_id,
    c.page_url,
    c.load_process
   FROM cte c
  WHERE (c.row_num = 1);

insert into wh.llm_processed_contents
("role",llm_date,url_id,prompt_id,persona_id,id,"object",created,model,"content",finish_reason,prompt_tokens,completion_tokens,total_tokens,record_id,load_id,load_date,load_process,page_url)
select distinct "role",llm_date,url_id,prompt_id,persona_id,id,"object",created,model,"content",finish_reason,prompt_tokens,completion_tokens,total_tokens,record_id,load_id,load_date,load_process,page_url
from dev.stg_llm_processed_subjgen_contents;

select "role",llm_date,url_id,prompt_id,persona_id,id,"object",created,model,"content",finish_reason,prompt_tokens,completion_tokens,total_tokens,record_id,load_id,load_date,load_process,page_url
from wh.llm_processed_contents;

select * from information_schema.views where table_name like '%v_llm_enriched_insights%'
select * from information_schema.views where view_definition like '%tbl_web_subject_content_master%'

select * from dev.v_llm_enriched_insights

select * from wh.tbl_web_content_categories;
drop table wh.tbl_web_content_categories;
create table wh.tbl_web_content_categories as select distinct * from dev.tbl_web_content_categories;
select count(*), count(distinct url_id)
from dev.tbl_subject_master_index4;
3152	2697

select count(*), count(distinct url_id)
from dev.tbl_subject_master_index;
3383	2697

select count(*) from wh.tbl_web_subject_content_master twscm 
 SELECT DISTINCT tsmi.record_id,
    tsmi.insight_id,
    tsmi.subject_id,
    tsmi.search_id,
    tsmi.url_id,
    tsmi.search_term,
    tsmi.page_url,
    tsmi.subject_title,
    tsmi.cluster_id,
    twcc.data_category,
    twcc.data_subject,
    md5((twcc.data_category)::text) AS data_category_id,
    md5(twcc.data_subject) AS data_subject_id
   FROM (dev.tbl_subject_master_index4 tsmi
     JOIN dev.tbl_web_content_categories twcc ON (((tsmi.url_id)::text = (twcc.url_id)::text)));


 SELECT DISTINCT tsmi.insight_id||subject_id||tsmi.url_id as record_id,
    tsmi.insight_id,
    tsmi.subject_id,
    tsmi.search_id,
    tsmi.url_id,
    tsmi.search_term,
    tsmi.page_url,
    tsmi.subject_title,
    	.cluster_id,
    twcc.data_category,
    twcc.data_subject,
    md5((twcc.data_category)::text) AS data_category_id,
    md5(twcc.data_subject) AS data_subject_id
   FROM (wh.tbl_web_subject_content_master tsmi
     JOIN dev.tbl_web_content_categories twcc ON (((tsmi.url_id)::text = (twcc.url_id)::text)));
select * from wh.tbl_web_subject_content_master;
select count(*), count(distinct img_cache.img_url_id)

select *
from dev.v_stg_image_cache img_cache
left join wh.tbl_web_content_img_master twcim
on img_cache.img_url_id = twcim.img_url_id
where twcim.img_url_id is null;

select count(*), count(distinct img_url_id)
from wh.tbl_web_content_img_master twcim 

select * from dev.v_content_media_cluster;
alter table wh.tbl_web_content_video_masser rename to tbl_web_content_video_master
create table wh.tbl_web_content_video_masser
as
 SELECT DISTINCT api_res.subject_id,
    api_res.insight_id,
    api_res.search_id,
    api_res.page_url,
    api_res.search_term,
    api_res.subject_title,
    api_res.url_id,
    api_res.record_id,
    api_res.videourl AS vid_url,
    api_res.title AS vid_title,
    md5(api_res.videourl) AS vid_url_id,
    COALESCE(COALESCE(COALESCE(COALESCE(img_cache.img_url, api_res.thumbnail)))) AS vid_thumb,
    md5(api_res.thumbnail) AS vid_thumb_id,
    api_res.title,
    api_res.description,
    twcc.data_category,
    twcc.data_subject,
    md5((twcc.data_category)::text) AS data_category_id,
    md5(twcc.data_subject) AS data_subject_id
   FROM ((dev.v_youtube_api_results api_res
     LEFT JOIN wh.tbl_web_content_img_master img_cache ON ((api_res.vid_thumb_id = img_cache.img_url_id)))
     LEFT JOIN dev.tbl_web_content_categories twcc ON (((api_res.url_id)::text = (twcc.url_id)::text)));
    

select distinct
 v_index.cluster_id
,v_index.url_id 
,v_index.subject_id 
,cat.data_category
,cat.data_subject
,md5(cat.data_category) as data_category_id
,md5(cat.data_subject) as data_subject_id
,v_index.subject_title 
,v_index.page_url 
,(feat.images -> 0) ->> 'img_url' AS featured_image_id
,media.images  -- JSON: [{"img_src": "wiki", "img_url": "https://upload.wikimedia.org/wikipedia/commons/0/0f/VAFB_Space_Launch_Complex-3_East_Atlas_V_2008-03-12.jpg"}, {"img_src": "wiki", "img_url": "https://upload.wikimedia.org/wikipedia/commons/6"}]
,feat.images as featured_images -- JSON: [{"img_url": "http:www.google.com", "img_src", "flickr"}, {"img_url": "http:www.flcikr.com", "img_src", "youtube"}], 
,media.videos --JSON: [{"vid_seq": 1, "vid_url": "https://www.youtube.com/watch?v=00fXmv9xpOg", "vid_thumb": "https://i.ytimg.com/vi/00fXmv9xpOg/hqdefault.jpg", "vid_title": "Go for Launch"}, {"vid_seq": 1, "vid_url": "https://www.youtube.com/watch?v=0HUwK1LkjgQ", "vid_thumb": "https://i.ytimg.com/vi/0HUwK1LkjgQ/hqdefault.jpg", "vid_title": "Landsat 9- 2,000th Rocket Launch"}]
,related.related_topics --JSON: [{ 'related_url_id', '1234' ,'related_cluster_id', '578','related_title', 'related.subject_title' ,'related_category', 'related.data_category'}]
,txt.subject_content --text that will be going into an HTML container
FROM
    dev.v_subject_master_index v_index
JOIN dev.v_web_content_text txt
	on txt.url_id = v_index.url_id
JOIN dev.v_content_media_cluster media
	on v_index.cluster_id = media.cluster_id
JOIN dev.v_content_media_url feat
	on v_index.url_id = feat.url_id
join dev.tbl_web_content_categories cat
	on v_index.url_id = cat.url_id
join dev.v_web_content_related_topics related
	on v_index.url_id = related.url_id;

SELECT DISTINCT v_index.cluster_id,
    v_index.url_id,
    v_index.subject_id,
    cat.data_category,
    cat.data_subject,
    md5(cat.data_category::text) AS data_category_id,
    md5(cat.data_subject) AS data_subject_id,
    v_index.subject_title,
    v_index.page_url,
    img_url as default_img,
    media.images,
    feat.images AS featured_images,
    media.videos,
    related.related_topics,
    txt.subject_content
   FROM dev.v_subject_master_index v_index
     JOIN dev.v_web_content_text txt ON txt.url_id = v_index.url_id::text
     JOIN dev.v_content_media_cluster media ON v_index.cluster_id::text = media.cluster_id::text
     JOIN dev.v_content_media_url feat ON v_index.url_id::text = feat.url_id::text
     JOIN dev.tbl_web_content_categories cat ON v_index.url_id::text = cat.url_id::text
     JOIN dev.v_web_content_related_topics related ON v_index.url_id::text = related.url_id::text
     join dev.v_default_img_ref def_img on v_index.url_id = def_img.url_id

     
select count(*), count(distinct img_url)
from transform.tbl_web_content_img_master


select * from wh.tbl_web_content_img_master ;

create table transform.tbl_web_content_img_master
as
 select distinct x.insight_id,
    x.search_id,
    x.img_url,
    x.img_url_id,
    x.img_title,
    x.description1,
    x.description2,
    x.description3,
    x.data_source,
    x.data_category,
    x.data_category_id,
    x.data_subject,
    x.data_subject_id,
    x.img_seq
   FROM ( SELECT DISTINCT a.insight_id,
            a.search_id,
            COALESCE(COALESCE(COALESCE(COALESCE(img_cache.img_full, img_cache.img_large), img_cache.img_med), img_cache.img_small), b.image_url) AS img_url,
            b.img_url_id,
            a.subject_title AS img_title,
            b.description1,
            b.description2,
            b.description3,
            b.data_source,
            a.data_category,
            a.data_category_id,
            a.data_subject,
            a.data_subject_id,
            row_number() OVER (PARTITION BY b.img_url_id ORDER BY b.img_url_id) AS img_seq
           FROM ((dev.v_subject_master_index a
             JOIN dev.v_flickr_api_results b ON (((a.search_id)::text = (b.search_id)::text)))
             LEFT JOIN wh.tbl_web_content_img_master img_cache ON ((b.img_url_id = img_cache.img_url_id)))) x
  WHERE (x.img_seq = 1)
UNION
 SELECT DISTINCT a.insight_id,
    a.search_id,
    COALESCE(COALESCE(COALESCE(COALESCE(img_cache.img_full, img_cache.img_large), img_cache.img_med), img_cache.img_small), b.image_url) AS img_url,
    b.img_url_id,
    a.subject_title AS img_title,
    b.description1,
    b.description2,
    b.description3,
    b.data_source,
    a.data_category,
    a.data_category_id,
    a.data_subject,
    a.data_subject_id,
    row_number() OVER (PARTITION BY b.search_id ORDER BY b.img_url_id) AS img_seq
   FROM ((dev.v_subject_master_index a
     JOIN dev.v_wiki_api_results b ON (((a.url_id)::text = b.url_id)))
     LEFT JOIN wh.tbl_web_content_img_master img_cache ON ((b.img_url_id = img_cache.img_url_id)));     

    
  SELECT tsmi.cluster_id,
    COALESCE(jsonb_agg(DISTINCT img.json_object) FILTER (WHERE (img.json_object IS NOT NULL)), '[]'::jsonb) AS images,
    COALESCE(jsonb_agg(DISTINCT vid.json_object) FILTER (WHERE (vid.json_object IS NOT NULL)), '[]'::jsonb) AS videos
   FROM (((dev.v_subject_master_index tsmi
     JOIN dev.v_web_content_text txt ON (((txt.subject_id = (tsmi.subject_id)::text) AND ((txt.search_id)::text = (tsmi.search_id)::text) AND (txt.url_id = (tsmi.url_id)::text))))
     LEFT JOIN LATERAL ( SELECT v_web_content_img.search_id,
            jsonb_build_object('img_url_id', v_web_content_img.img_url_id, 'img_url', v_web_content_img.img_url, 'img_src', v_web_content_img.data_source, 'img_title', v_web_content_img.img_title, 'img_desc1', v_web_content_img.description1, 'img_desc2', v_web_content_img.description2) AS json_object
           FROM dev.v_web_content_img
          WHERE ((v_web_content_img.data_source IS NOT NULL) AND (v_web_content_img.img_url_id IS NOT NULL))
          GROUP BY v_web_content_img.search_id, v_web_content_img.img_url_id, v_web_content_img.img_url, v_web_content_img.data_source, v_web_content_img.img_title, v_web_content_img.description1, v_web_content_img.description2, v_web_content_img.description3) img ON (((img.search_id)::text = (tsmi.search_id)::text)))
     LEFT JOIN LATERAL ( SELECT v_web_content_video.search_id,
            jsonb_build_object('vid_url_id', v_web_content_video.vid_url_id, 'vid_thumb_id', v_web_content_video.vid_thumb_id, 'vid_thumb_url', v_web_content_video.vid_thumb, 'vid_title', v_web_content_video.vid_title, 'vid_url', v_web_content_video.vid_url) AS json_object
           FROM dev.v_web_content_video
          WHERE ((v_web_content_video.vid_url_id IS NOT NULL) AND (v_web_content_video.vid_title IS NOT NULL))
          GROUP BY v_web_content_video.search_id, v_web_content_video.vid_url_id, v_web_content_video.vid_thumb_id, v_web_content_video.vid_thumb, v_web_content_video.vid_title, v_web_content_video.vid_url) vid ON (((vid.search_id)::text = (tsmi.search_id)::text)))
  GROUP BY tsmi.cluster_id;

select data_category, count(*), count(distinct url_id)
from  dev.v_wiki_api_results
group by data_category;

select count(*), count(distinct url_id)
from dev.v_llm_api_prompt_source_places;
842	742
708	638
645	594
295	278
297	276
212	202

select count(*), count(distinct url_id)
from dev.v_llm_api_prompt_source;
408	381
357	338
275	264
209	199
78	65
46	38

select * from dev.llm_processed_contents;
select count(*), count(distinct url_id)
from dev.stg_llm_processed_subjgen_contents slpsc;
846	845
994	993
1133	1132
1256	1255
1644	1643
1771	1770
select * from information_schema.views where table_name = 'v_llm_api_prompt_source'

select * from wh.tbl_web_content_feed_master twcfm 
where default_img like '%7000ddfe9ed23c68b0b17eb8293100ae%'


create or replace view dev.v_llm_api_prompt_source_places as
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
   FROM (( SELECT x.prompt_id,
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
                          WHERE ((a.persona_id = 2) AND (b.prompt_id = 1))
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
                   FROM ((dev.v_web_content_text ws
                     JOIN dev.v_wiki_api_results wiki ON ((((ws.insight_id)::text = (wiki.insight_id)::text) AND (ws.page_url = wiki.page_url))))
                     CROSS JOIN llm_prompt lp)
                  WHERE ((wiki.data_category)::text like '%places%'::text)
                  ORDER BY ws.page_url) x
          ORDER BY (random())
         LIMIT 1000) z
     LEFT JOIN dev.stg_llm_processed_subjgen_contents subjgen ON ((z.url_id = subjgen.url_id)))
  WHERE (subjgen.url_id IS null
 and replace(substr(text_chunk, 0, 50), ' ', '') not like '**%'
  );
 
 
SELECT prompt_id, prompt_template_user, prompt_template_system, prompt_key, llm_role, llm_expertise, llm_goal, llm_goal_desc, prompt_type, prompt_intro, prompt_description, data_output_profile, data_source, key_concepts, persona_id, occupation, interests, audiencedesc,trait1, trait2, trait3, trait4, trait5, url_id, search_term, subj_title, category, page_url, text_chunk FROM dev.v_llm_api_prompt_source limit 5
select cluster_id, count(*)
from wh.tbl_web_content_feed_master
group by cluster_id;

select 
cluster_id, url_id, subject_id, subject_title, default_img, data_category, data_category_id, data_subject, data_subject_id, images, videos, featured_images, related_topics, subject_content, content_name
from wh.tbl_web_content_feed_master

select data_category, count(*)
from dev.stg_wiki_api_results swar 
group by data_category;

select category, count(*)
from dev.stg_wiki_api_results 
group by category;

select * from dev.stg_llm_processed_subjgen_contents
where content like '%rocket%'
order by load_date desc;

select url_id, count(*)
from  dev.stg_llm_processed_subjgen_contents
group by url_id 
having count(url_id) > 1;

SELECT prompt_id, prompt_template_user, prompt_template_system, prompt_key, llm_role, llm_expertise, llm_goal, llm_goal_desc, prompt_type, prompt_intro, prompt_description
, data_output_profile, data_source, key_concepts, persona_id, occupation, interests, audiencedesc,trait1, trait2, trait3
, trait4, trait5, url_id, search_term, subj_title, category, page_url, text_chunk 
FROM dev.v_llm_api_prompt_source limit 5

truncate table dev.stg_llm_processed_subjgen_contents;
insert into dev.stg_llm_processed_subjgen_contents select distinct "role",llm_date,url_id,prompt_id,persona_id,id,"object",created,model,"content",finish_reason,prompt_tokens,completion_tokens,total_tokens,record_id,load_id,load_date,load_process,page_url from dev.dedup_stg_llm_processed_subjgen_contents
CREATE TABLE dev.dedup_stg_llm_processed_subjgen_contents AS
WITH RankedData AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY url_id ORDER BY load_date DESC) AS row_num
    FROM dev.stg_llm_processed_subjgen_contents
)
SELECT
    *
FROM RankedData
WHERE row_num = 1;


select *
from  dev.stg_llm_processed_subjgen_contents
where url_id = '76d1ee5a0d311a0052aa68a2e6a42118'

select model, count(*)
from dev.stg_llm_processed_subjgen_contents slpsc 
group by model
order by count(*) desc;

-- dev.v_llm_api_prompt_source source

		
		create table dev.stg_llm_processed_subjgen_contents
		as select * from dev.llm_processed_contents lpc where 0=1

select * from dev.stg_llm_processed_subjgen_contents lpc 

-- wh.v_web_content_feed_master source

CREATE OR REPLACE VIEW wh.v_web_content_feed_master
AS SELECT DISTINCT a.cluster_id,
    a.url_id,
    a.subject_id,
    a.subject_title,
    a.default_img,
    a.data_category,
    a.data_category_id,
    a.data_subject,
    a.data_subject_id,
    a.images,
    a.videos,
    a.featured_images,
    a.related_topics,
    COALESCE(b.subject_content, a.subject_content) AS subject_content,
    a.data_category AS content_name
   FROM wh.tbl_web_feed_master a
     LEFT JOIN wh.tbl_web_subject_content_master b ON a.url_id::text = b.url_id
  WHERE lower(a.default_img) !~~ '%.jpeg%'::text;

 select * from wh.v_web_content_feed_master
 where url_id='7dadc5abfe2377505d05a6a2c2ac718e'

select * from dev.v_llm_base_prompts vlbp 
select * from dev.llm_base_prompts lbp 
select * from dev.llm_proto_prompt lpp 
create table dev.llm_base_prompts_11162024
as select * from dev.llm_base_prompts lbp 

update dev.llm_proto_prompt
set prompt_template_system = 
'
### **GLOBAL PROMPT FOR ASSISTANT DIRECTIONS **
Create an educational blog post for a student researcher with:
- A succinct intro
- 3 numbered bullet points summarizing key facts
- New factual information related to @@_category_@@
- Extending WIP_STARTER_TEXT text content with factual content
- Use WIP_STARTER_TEXT as the base source and generate a story according to all known and stated objectives

Take your time and think step by step.
---

**YOUR Role and Expertise:**
You are a [@@_category_@@] researcher with special skills in **Content Editor**, **Python Engineer** data wrangling
You take in content and you improve it using your deep knowledge of @@_category_@@
You always remember your audience and goals and skills while performing your work
You never repeat instructions within the content

**YOUR Audience Description:**
Interests: @@_interests_@@
Audience Description: @@_audiencedesc_@@
Occupation: @@_occupation_@@
Audience Traits: @@_trait1_@@, @@_trait2_@@, @@_trait3_@@, @@_trait4_@@, @@_trait5_@@
**YOUR Objective & Goal**

 Review these details about content and goals and execute faithfully against goals as your role demands.
 Content Editor, Blog post editor, Data engineer/web scraping.
 EXPERTISE: [@@_category_@@]

 Add a header and ensure a few bullets exist describing @@_category_@@.   
 Augment and add new detail that is factual and relevant.  
 Use trusted web resoures and other knowledge banks related to category and subject such as Wikipedia.
 Remember you are an expert on @@_category_@@ and the specific SUBJECT given to you

**OUTPUT Instructions:**
1. **Header Formatting:**
   - Begin with a header using bold markdown style (`**Bold Header Text**`), followed by a new line.
2. **Paragraph Structuring:**
   - Break the text content into paragraphs, each separated by new lines for clarity and readability.
3. **List Formatting:**
   - Format any lists into consistent, standard bulleted lists with bold numbers (e.g., **1.**), each item starting on a new line.
4. **Content Cleaning:**
   - Remove any leading quotes, hash symbols (`#`), or the string value "html" within the first 10 bytes of the content.
5. **Content Integrity:**
   - Retain all meaningful original content to ensure comprehension.
   - Do not lose any information or repeat instructions.

**Formatting Requirements:**
- Ensure the content is cohesive and formatted appropriately for an educational blog post aimed at **AUDIENCE** regarding **@@_category_@@**,
**Penalty Notice:**
- There is a penalty for losing information/content or repeating instructions.
- overusing words like [Delving], [Diving in], [Enchanting] or other overly dramatic descriptive language.  Be informative and descriptive.
'
where prompt_id = 1;
select count(*), count(distinct url_id) from dev.llm_processed_contents
where content not like '**%'

select count(*)
from dev.v_llm_api_prompt_source
where text_chunk not like '**%'


select * from dev.stg_llm_processed_contents slpc 
select * from dev.stg_llm_processed_contents_test_data slpctd 
delete from dev.stg_llm_processed_contents where url_id in (select url_id from dev.stg_llm_processed_contents_test_data)
select * from dev.v_llm_api_hygiene_source vlahs 
create table wh.tbl_web_subject_content_master
as
SELECT DISTINCT 
    wiki.subject_id,
    wiki.insight_id,
    wiki.search_id,
    wiki.page_url,
    wiki.search_term,
    wiki.subject_title,
    wiki.url_id,
    -- Use COALESCE to replace NULL llm_reply with a default value
    COALESCE(hygiene.llm_reply, feed.subject_content, insights.llm_reply, 'No Reply Available') AS subject_content,
    wiki.data_source
FROM dev.v_wiki_api_results AS wiki
LEFT JOIN dev.v_llm_hygiene_results AS hygiene
    ON wiki.url_id = hygiene.url_id
LEFT JOIN wh.tbl_web_feed_master AS feed
    ON wiki.url_id = feed.url_id
LEFT JOIN dev.v_llm_enriched_insights AS insights
    ON wiki.url_id = insights.url_id;


select * from wh.tbl_web_feed_master;
	  

select * from dev.stg_llm_processed_contents
where content like '*%'
and content not like '**%'

select * 
from dev.stg_llm_processed_contents
where content like '#%'

select * from 
dev.v_llm_api_prompt_source;

select * from dev.v_llm_api_prompt_source;

CREATE OR REPLACE VIEW dev.v_wiki_api_results
AS SELECT DISTINCT stg_wiki_api_results.wiki_result_id AS insight_id,
    stg_wiki_api_results.resultid AS result_id,
    md5(stg_wiki_api_results.subjtitle) AS subject_id,
    md5(stg_wiki_api_results.pageurl) AS url_id,
    md5(stg_wiki_api_results.imageurl) AS img_url_id,
    md5(stg_wiki_api_results."extract") AS content_id,
    'wiki'::text AS data_source,
    stg_wiki_api_results.subjtitle AS subject_title,
    stg_wiki_api_results."extract" AS subject_content,
    stg_wiki_api_results.searchterm AS search_term,
    stg_wiki_api_results.searchid AS search_id,
    stg_wiki_api_results.category AS data_category,
    regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(stg_wiki_api_results.imageurl, '^.*/([^/]+)\.(jpg|jpeg|png|gif|JPG|JPEG)$'::text, '\1'::text), '%2B'::text, chr(43), 'g'::text), '%3D'::text, chr(61), 'g'::text), '%40'::text, chr(64), 'g'::text), '%3F'::text, chr(63), 'g'::text), '%2F'::text, chr(47), 'g'::text), '%3A'::text, chr(58), 'g'::text), '%20'::text, ' '::text, 'g'::text), '%2C'::text, ','::text, 'g'::text), '%29'::text, ')'::text, 'g'::text), '%28'::text, '('::text, 'g'::text), '%26'::text, '&'::text, 'g'::text), '%27'::text, chr(39), 'g'::text), '[_]'::text, ' '::text, 'g'::text) AS description1,
    stg_wiki_api_results.subjtitle AS description2,
    stg_wiki_api_results.searchterm AS description3,
    stg_wiki_api_results.pageurl AS page_url,
    stg_wiki_api_results.imageurl AS image_url,
    stg_wiki_api_results.wiki_result_id,
    stg_wiki_api_results.load_date,
    stg_wiki_api_results.load_id
   FROM dev.stg_wiki_api_results
  WHERE length(TRIM(BOTH FROM stg_wiki_api_results.imageurl)) > 0;
tbl_web_feed_master
 select count(*) from dev.v_llm_enriched_insights;

select *  from dev.stg_llm_processed_contents
order by LLM_DATE desc;
select count(*), count(distinct url_id)
from dev.stg_llm_processed_contents;
 --1782	977
--1795	988
--1797	990
--1818	1011
--1842	1035
--1855	1048
--1881	1074
--1944	1137
--2025	1218
--2091	1284
--582	326 8:28 PM
--622	355 8:39 PM
--663	391 10:25 PM
--663	391 7:56 AM
--733	400 8:23 AM 
--881	748
--944	809
insert into dev.stg_llm_processed_contents (select distinct * from dev.stg_llm_processed_contents_bkup)

--#########################
---GPT 3.5 switch
--#################
--752	418 8:29AM
--818   477 8:53AM
--1520	776 
--1581	776
--1583	778
--1593	788
--1612	807
--1624	819
--1660	855 12:32PM
--1705	900 12:53 PM - config file changes
--1714	909
--1750	945 - config file changes 
--1750	945
--1750	945
--
update dev.llm_proto_prompt 
set prompt_template_user=
'----audience and topic reference-----
YOUR EXPERTISE: @@_llm_expertise_@@
THIS SUBJECT_CATEGORY: @@_category_@@

---- current objective/goals -----
ROLE: @@_llm_role_@@

@@_prompt_intro_@@

OBJECTIVE:
@@_llm_goal_desc_@@

Reminders: 
@@_key_concepts_@@
@@_data_output_profile_@@

----WIP_STARTER_TEXT TO REGENERATE BELOW -----

@@_text_chunk_@@'
where prompt_id=3;
insert into dev.stg_llm_processed_contents
(url_id, page_url, prompt_id, persona_id)
select url_id, page_url, prompt_id, persona_id 
select prompt_id, prompt_template_user, prompt_template_system, prompt_key, llm_role, llm_expertise, llm_goal, llm_goal_desc, prompt_type, prompt_intro, prompt_description, data_output_profile, data_source, key_concepts, persona_id, occupation, interests, audiencedesc,trait1, trait2, trait3, trait4, trait5, url_id, search_term, subj_title, category, page_url, text_chunk
from 
dev.v_llm_api_hygiene_source
where url_id = '0019cd808140c9463a54af48b538b948'


create table dev.stg_llm_processed_contents_test_data
as select * from dev.stg_llm_processed_contents slpc limit 1000

delete from dev.stg_llm_processed_contents where url_id in (select url_id from dev.stg_llm_processed_contents_test_data);
select count(*) from dev.v_llm_api_hygiene_source;
--1105
--277

select url_id from dev.v_llm_api_hygiene_source
limit 5

CREATE OR REPLACE VIEW dev.v_llm_api_hygiene_source AS 
SELECT 
        unfiltered.prompt_id,
        unfiltered.prompt_id as prompt_key,
        llm_role,
        llm_expertise,
        llm_goal,
        llm_goal_desc,
        prompt_type,
        prompt_intro,
        prompt_description,
        data_output_profile,
        data_source,
        key_concepts,
        prompt_template_user,
        prompt_template_system,
        unfiltered.persona_id,
        occupation,
        interests,
        audiencedesc,
        trait1,
        trait2,
        trait3,
        trait4,
        trait5,
        unfiltered.url_id,
        search_term,
        subj_title,
        category,
        unfiltered.page_url,
        text_chunk
        FROM (
    SELECT DISTINCT 
        z.prompt_id,
        z.prompt_id as prompt_key,
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
    FROM (
        SELECT x.prompt_id,
            x.prompt_id as prompt_key,
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
        FROM (
            WITH llm_prompt AS (
                SELECT DISTINCT 
                    b.prompt_id AS prompt_id,
                    b.prompt_id as prompt_key,
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
                FROM dev.v_llm_persona a
                JOIN dev.v_llm_base_prompts b ON a.persona_id = 3 AND b.prompt_id = 3
            )
            SELECT DISTINCT 
                lp.prompt_id,
                lp.prompt_id as prompt_key,
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
            JOIN dev.v_wiki_api_results wiki 
                ON ws.insight_id::text = wiki.insight_id::text 
                AND ws.page_url = wiki.page_url
            CROSS JOIN llm_prompt lp
            ORDER BY ws.page_url
        ) x
        ORDER BY random()
        -- LIMIT 1
    ) z
) unfiltered
LEFT JOIN dev.stg_llm_processed_contents stg_llm ON unfiltered.page_url = stg_llm.page_url
WHERE stg_llm.page_url IS NULL 
  AND (
      unfiltered.text_chunk LIKE '#%' 
      OR unfiltered.text_chunk LIKE '*%'
      OR unfiltered.text_chunk LIKE '%<strong>%'
      OR unfiltered.text_chunk LIKE '%<b>%'
      OR unfiltered.text_chunk LIKE '%<html>%'
      OR unfiltered.text_chunk LIKE '%<style%'
      OR POSITION('html' IN SUBSTR(unfiltered.text_chunk, 1, 10)) > 0
  )
 ORDER BY random();


select * from information_schema.views where table_name like '%v_wiki_api_results%'

select 
count(*) 
,count(case when text_chunk like '**%' then  url_id  end)
,count(case when text_chunk not like '**%' then url_id end)
from  dev.v_llm_api_prompt_source 

from  wh.tbl_web_content_feed_master

create or replace view dev.v_wiki_api_results as
 SELECT DISTINCT a.wiki_result_id AS insight_id,
    a.resultid AS result_id,
    md5(a.subjtitle) AS subject_id,
    md5(a.pageurl) AS url_id,
    md5(a.imageurl) AS img_url_id,
    md5(a."extract") AS content_id,
    'wiki'::text AS data_source,
    a.subjtitle AS subject_title,
    coalesce(b.subject_content, a."extract") AS subject_content,
    a.searchterm AS search_term,
    a.searchid AS search_id,
    a.category AS data_category,
    regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(a.imageurl, '^.*/([^/]+)\.(jpg|jpeg|png|gif|JPG|JPEG)$'::text, '\1'::text), '%2B'::text, chr(43), 'g'::text), '%3D'::text, chr(61), 'g'::text), '%40'::text, chr(64), 'g'::text), '%3F'::text, chr(63), 'g'::text), '%2F'::text, chr(47), 'g'::text), '%3A'::text, chr(58), 'g'::text), '%20'::text, ' '::text, 'g'::text), '%2C'::text, ','::text, 'g'::text), '%29'::text, ')'::text, 'g'::text), '%28'::text, '('::text, 'g'::text), '%26'::text, '&'::text, 'g'::text), '%27'::text, chr(39), 'g'::text), '[_]'::text, ' '::text, 'g'::text) AS description1,
    a.subjtitle AS description2,
    a.searchterm AS description3,
    a.pageurl AS page_url,
    a.imageurl AS image_url,
    a.wiki_result_id,
    a.load_date,
    a.load_id
   FROM dev.stg_wiki_api_results a
    join wh.tbl_web_content_feed_master b
   on md5(a.pageurl) = b.url_id
  WHERE (length(TRIM(BOTH FROM a.imageurl)) > 0);

select * from wh.tbl_web_content_feed_master ;
select * from information_schema.views where table_name = 'v_llm_enriched_insights'



