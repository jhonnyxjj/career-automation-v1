export type CandidateProfile = {
  id: string;
  personal: { name: string; headline?: string | null };
  technical_skills: { category: string; items: string[] }[];
};

export type JobListing = {
  source: string;
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
};

export type JobMatch = {
  id: string;
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
  sourceUrl: string;
  listing: JobListing;
};

export type SearchFilters = {
  seniorities: string[];
  regions: string[];
  workModes: string[];
  limit: string;
};

export type GeneratedResume = { id: string; pdf_available: boolean };
