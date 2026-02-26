  select count(*) from dev.stg_flickr_api_results;
  select count(*) from dev.stg_youtube_api_results;
  select count(*) from dev.stg_wiki_api_results;

/************
 ************
 *  STAGING
 *************
 *************/

/* tables */
dev.stg_wiki_api_results
dev.stg_flickr_api_results
dev.stg_youtube_api_results
dev.stg_img_cache

/* views */ 
dev.v_youtube_api_results
dev.v_wiki_api_results
dev.v_flickr_api_results
dev.v_stg_image_cache

/************
 ************
 * MIDDLE TIER
 *************
 *************/
/* tables */
dev.tbl_web_content_categories
dev.tbl_web_content_img_master
dev.llm_proto_prompt 
dev.llm_base_prompts
dev.llm_persona

/* views */
dev.v_subject_master_index
dev.v_web_content_text
dev.v_content_media_subject

dev.v_web_content_img_master
dev.v_web_content_video
dev.v_default_img_ref
dev.v_web_content_img
dev.v_content_media_cluster
dev.v_web_content_img_cache
dev.v_content_media_url
dev.v_content_media_category

dev.v_llm_api_prompt_source
dev.v_llm_persona
dev.v_llm_base_prompts
dev.v_llm_enriched_insights

/************
 ************
 * WAREHOUSE
 *************
 *************/
/* tables */
wh.tbl_web_content_img_cache_0527
wh.tbl_web_feed_master

/* views */
wh.v_web_content_feed_master
wh.v_web_content_img_cache

/*********************/
select * from information_schema.views 
where view_definition like '%v_web_content_video%'

