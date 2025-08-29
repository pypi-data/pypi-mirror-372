from enum import Enum

class ArtifactSortBy(str, Enum):
    GroupId = "groupId",
    ArtifactId = "artifactId",
    CreatedOn = "createdOn",
    ModifiedOn = "modifiedOn",
    ArtifactType = "artifactType",
    Name = "name",

