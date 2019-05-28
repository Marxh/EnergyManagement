select * from `LineDetection_article`,
(select `LineDetection_article_tag_on`.article_id, `LineDetection_article_tag_on`.tag_id, 
`LineDetection_tag`.facility_id_id, `LineDetection_tag`.tag_text
from `LineDetection_article_tag_on` left join `LineDetection_tag` on LineDetection_article_tag_on.tag_id = LineDetection_tag.id
where LineDetection_tag.facility_id_id= {% facility_id %}) as T1
where LineDetection_article.id = T1.article_id