from enum import Enum

class VersionSortBy(str, Enum):
    GroupId = "groupId",
    ArtifactId = "artifactId",
    Version = "version",
    Name = "name",
    CreatedOn = "createdOn",
    ModifiedOn = "modifiedOn",
    GlobalId = "globalId",

