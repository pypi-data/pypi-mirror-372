from dataclasses import dataclass, asdict

@dataclass
class GitLabApplicationStats():
   forks: str
   issues: str
   merge_requests: str
   notes: str
   snippets: str
   ssh_keys: str
   milestones: str
   users: str
   groups: str
   projects: str
   active_users: str

   def to_dict(self):
      return asdict(self)
