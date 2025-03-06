import pandas as pd
import logging
from typing import Tuple, Dict, List

class DiscussionDataProcessor:
    @staticmethod
    def process_discussion_data(data: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Process raw discussion data into structured DataFrames"""
        participants = data.get('participants', [])
        view = data.get('view', [])
        
        df_participants = pd.DataFrame(participants)
        posts = DiscussionDataProcessor._extract_posts_and_replies(view)
        df_posts = pd.DataFrame(posts)
        
        return DiscussionDataProcessor._merge_participant_data(df_participants, df_posts)
    
    @staticmethod
    def _extract_posts_and_replies(view: List[Dict]) -> List[Dict]:
        """Extract posts and replies from view data"""
        posts = []
        for post in view:
            if 'user_id' in post:
                posts.append(DiscussionDataProcessor._create_post_dict(post, 'post'))
            
            for reply in post.get('replies', []):
                if 'user_id' in reply:
                    posts.append(DiscussionDataProcessor._create_post_dict(reply, 'reply'))
        return posts
    
    @staticmethod
    def _create_post_dict(post: Dict, post_type: str) -> Dict:
        """Create standardized post dictionary"""
        return {
            'post_id': post['id'],
            'user_id': post['user_id'],
            'parent_id': post.get('parent_id'),
            'created_at': post['created_at'],
            'updated_at': post['updated_at'],
            'message': post['message'],
            'type': post_type
        }
    
    @staticmethod
    def _merge_participant_data(df_participants: pd.DataFrame, 
                              df_posts: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Merge participant data with posts"""
        if not df_posts.empty and not df_participants.empty:
            df_posts = df_posts.merge(
                df_participants[['id', 'display_name']], 
                left_on='user_id', 
                right_on='id', 
                how='left'
            )
            df_posts.drop('id', axis=1, inplace=True)
        return df_participants, df_posts 