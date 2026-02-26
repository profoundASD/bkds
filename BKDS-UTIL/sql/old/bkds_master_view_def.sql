"CREATE OR REPLACE VIEW dev.v_llm_base_prompts AS  WITH cte AS (
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
  WHERE c.row_num = 1;;"

";"
"CREATE OR REPLACE VIEW dev.v_web_content_text AS  SELECT DISTINCT a.subject_id,
    a.insight_id,
    a.search_id,
    a.page_url,
    a.search_term,
    a.subject_title,
    a.url_id,
    a.content_id,
        CASE
            WHEN length(TRIM(BOTH FROM b.llm_reply)) > 0 AND b.llm_reply IS NOT NULL THEN concat_ws('

'::text, b.llm_reply, '***original content below***', a.subject_content)
            ELSE a.subject_content
        END AS subject_content,
    a.data_source
   FROM dev.v_wiki_api_results a
     LEFT JOIN dev.v_llm_enriched_insights b ON a.url_id = b.url_id;;"
"CREATE OR REPLACE VIEW dev.delete_v_subject_index_prev AS  WITH subj_index AS (
         SELECT x.record_id,
            x.category,
            x.keyword,
            x.subject,
            x.category_id,
            x.search_id,
            x.subject_id,
            x.src_subject,
            x.src_category,
            x.src_keyword,
            x.load_date,
            x.load_process,
            x.load_id,
            x.load_file,
            x.file_id,
            row_number() OVER (PARTITION BY x.record_id ORDER BY x.load_date DESC) AS row_num
           FROM dev.bkup_tbl_subject_index x
        )
 SELECT DISTINCT subj_index.record_id AS insight_id,
    subj_index.category,
    subj_index.subject,
    subj_index.keyword,
    subj_index.src_keyword AS search_term,
    subj_index.category_id,
    subj_index.subject_id,
    subj_index.search_id,
    subj_index.load_date,
    subj_index.load_process,
    subj_index.load_id,
    subj_index.load_file,
    subj_index.file_id
   FROM subj_index
  WHERE subj_index.row_num = 1;;"
";"
"CREATE OR REPLACE VIEW dev.v_subject_master_index AS  SELECT DISTINCT tsmi.record_id,
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
    md5(twcc.data_category::text) AS data_category_id,
    md5(twcc.data_subject) AS data_subject_id
   FROM dev.tbl_subject_master_index4 tsmi
     JOIN dev.tbl_web_content_categories twcc ON tsmi.url_id::text = twcc.url_id::text;;"
"CREATE OR REPLACE VIEW dev.v_pids AS  SELECT pg_stat_activity.pid,
    pg_stat_activity.query_start,
    pg_stat_activity.state,
    pg_stat_activity.usename,
    pg_stat_activity.datname,
    "substring"(pg_stat_activity.query, 1, 50) AS query_snippet
   FROM pg_stat_activity
  WHERE pg_stat_activity.state = 'active'::text;;"

"CREATE OR REPLACE VIEW dev.v_web_content_img_cache1 AS  SELECT v_web_content_img_cache.img_url_id,
    v_web_content_img_cache.data_source,
    v_web_content_img_cache.img_type,
    v_web_content_img_cache.img_url
   FROM wh.v_web_content_img_cache
 LIMIT 10000;;"
"CREATE OR REPLACE VIEW dev.delete_v_subject_index AS  WITH subj_index AS (
         SELECT nextval('seq_tbl_subject_master_index'::regclass) AS record_id,
            x.insight_id,
            x.search_id,
            x.data_category,
            x.search_term,
            x.src_subject_id AS subj_key,
            x.data_subject,
            x.page_url AS orig_page_url,
            md5(x.page_url) AS url_id,
            x.load_date,
            x.load_process,
            x.load_id,
            x.load_file,
            x.file_id,
            row_number() OVER (PARTITION BY x.search_term ORDER BY x.load_date DESC) AS row_num
           FROM dev.tbl_subject_master_index_0423 x
        )
 SELECT DISTINCT subj_index.insight_id,
    subj_index.record_id,
    subj_index.search_id,
    subj_index.data_category,
    subj_index.search_term,
    subj_index.subj_key,
    subj_index.data_subject,
    subj_index.orig_page_url,
    subj_index.url_id,
    subj_index.load_date,
    subj_index.load_process,
    subj_index.load_id,
    subj_index.load_file,
    subj_index.file_id
   FROM subj_index
  WHERE subj_index.row_num = 1;;"
"CREATE OR REPLACE VIEW dev.v_web_content_img_cache2 AS  SELECT DISTINCT a.img_url_id,
    a.data_source,
    a.img_type,
    a.img_url
   FROM wh.v_web_content_img_cache a
     LEFT JOIN dev.v_web_content_img_cache1 b ON a.img_url_id = b.img_url_id
  WHERE b.img_url_id IS NULL
 LIMIT 10000;;"
"CREATE OR REPLACE VIEW dev.tbl_web_content_img_cache3 AS  SELECT DISTINCT a.img_url_id,
    a.data_source,
    a.img_type,
    a.img_url
   FROM wh.v_web_content_img_cache a
     LEFT JOIN dev.v_web_content_img_cache2 b ON a.img_url_id = b.img_url_id
  WHERE b.img_url_id IS NULL
 LIMIT 10000;;"
"CREATE OR REPLACE VIEW dev.v_web_content_img_cache3 AS  SELECT DISTINCT a.img_url_id,
    a.data_source,
    a.img_type,
    a.img_url
   FROM wh.v_web_content_img_cache a
     LEFT JOIN dev.v_web_content_img_cache2 b ON a.img_url_id = b.img_url_id
  WHERE b.img_url_id IS NULL
 LIMIT 10000;;"
"CREATE OR REPLACE VIEW dev.v_subject_gen_source AS  SELECT x.insight_id,
    x.data_category,
    x.data_subject AS subject,
    x.subject_title,
    x.search_id,
    x.subject_id,
    x.search_term,
    x.orig_search_term
   FROM ( SELECT vsgs.insight_id,
            vsgs.data_category,
            vsgs.data_subject,
            vsgs.subject_title,
            vsgs.search_id,
            vsgs.subject_id,
            vsgs.subject_title AS search_term,
            vsgs.search_term AS orig_search_term,
            row_number() OVER (PARTITION BY vsgs.insight_id ORDER BY vsgs.load_date DESC) AS row_num
           FROM dev.tbl_subject_master_index vsgs) x
  WHERE x.row_num = 1;;"
";"
";"
"CREATE OR REPLACE VIEW dev.v_web_content_insights AS  SELECT DISTINCT tsmi.insight_id,
    tsmi.search_id,
    tsmi.subject_id,
    tsmi.subject_title,
    tsmi.search_term,
    tsmi.data_category,
    tsmi.data_subject
   FROM dev.tbl_subject_master_index tsmi;;"

""
";"
";"

";"
";"
"CREATE OR REPLACE VIEW dev.v_web_content_img_cache AS  SELECT img_master.img_url_id,
    img_master.data_source,
    img_master.img_type,
    img_master.img_url
   FROM ( SELECT DISTINCT v_web_content_video.vid_thumb_id AS img_url_id,
            'youtube'::text AS data_source,
            'thumbnail'::text AS img_type,
            v_web_content_video.vid_thumb AS img_url
           FROM dev.v_web_content_video
        UNION
         SELECT DISTINCT v_web_content_img.img_url_id,
            v_web_content_img.data_source,
            'gallery'::text AS img_type,
            v_web_content_img.img_url
           FROM dev.v_web_content_img) img_master
     LEFT JOIN dev.stg_img_cache img_cache ON img_master.img_url_id = img_cache.img_url_id::text
  WHERE img_cache.img_url_id IS NULL;;"

";"
"CREATE OR REPLACE VIEW dev.v_web_feed_master AS  SELECT DISTINCT v_index.cluster_id,
    v_index.url_id,
    v_index.subject_id,
    cat.data_category,
    cat.data_subject,
    md5(cat.data_category::text) AS data_category_id,
    md5(cat.data_subject) AS data_subject_id,
    v_index.subject_title,
    v_index.page_url,
    def_img.img_url AS default_img,
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
     JOIN dev.v_default_img_ref def_img ON v_index.url_id::text = def_img.url_id;;"
"CREATE OR REPLACE VIEW dev.v_stg_image_cache AS  SELECT DISTINCT sic.img_url_id,
    sic.img_name,
    sic.img_type,
    sic.img_path,
    sic.img_small_path,
    sic.img_medium_path,
    sic.img_large_path,
    sic.data_source,
    sic.load_date,
    sic.load_proc,
    sic.load_key,
    sic.load_seq,
    sic.batch_id
   FROM dev.stg_img_cache sic
  WHERE sic.img_path !~~ '%_PIL_%'::text;;"