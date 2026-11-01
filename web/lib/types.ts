export type CandidateProfile = {
  id: string;
  personal: { name: string; headline?: string | null; city?: string | null; state?: string | null; email?: string | null; phone?: string | null; linkedin?: string | null; github?: string | null; portfolio?: string | null };
  professional_summary?: string | null;
  technical_skills: { category: string; items: string[] }[];
  experiences: { company: string; location?: string | null; position: string; period: string; bullets: string[] }[];
  projects: { name: string; context?: string | null; technologies: string[]; bullets: string[] }[];
  education: { institution: string; location?: string | null; course: string; period: string }[];
};

export type JobListing = {
  source: string;
  listing_type: "job" | "recruiter_post";
  title: string;
  company: string;
  url: string;
  external_id?: string | null;
  description?: string | null;
  location?: string | null;
  workplace_type?: string | null;
  seniority?: string | null;
  apply_url?: string | null;
  technologies: string[];
  score: number;
  score_version?: string | null;
  score_breakdown?: { label: string; points: number; status: "match" | "penalty" | "not_identified" | "unknown" }[];
  filter_accepted?: boolean | null;
  filter_reason?: string | null;
};

export type JobMatch = {
  id: string;
  source: string;
  listingType: "job" | "recruiter_post";
  title: string;
  company: string;
  location?: string;
  workMode?: string;
  technologies: string[];
  score: number;
  matchedRequirements: number;
  totalRequirements: number;
  missingSkills: string[];
  description?: string;
  requirements?: string[];
  originUrl: string;
  applyUrl?: string;
  listing: JobListing;
};

export type ManualJobImport = {
  source: string;
  listing_type: "job" | "recruiter_post";
  title: string;
  company: string;
  description: string;
  source_url: string;
  apply_url?: string;
  location?: string;
};

export type SearchFilters = {
  seniorities: string[];
  regions: string[];
  workModes: string[];
  limit: string;
};

export type GeneratedResume = { id: string; pdf_available: boolean };
