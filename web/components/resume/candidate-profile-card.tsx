import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CandidateProfile } from "@/lib/types";

export function CandidateProfileCard({ profile }: { profile: CandidateProfile }) {
  return (
    <Card>
      <CardHeader>
        <p className="text-sm text-muted-foreground">Perfil identificado</p>
        <CardTitle className="text-xl">{profile.personal.headline ?? profile.personal.name}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-2">
        {profile.technical_skills.flatMap((group) => group.items).map((technology) => <Badge key={technology} variant="secondary">{technology}</Badge>)}
      </CardContent>
    </Card>
  );
}
