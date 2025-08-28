from pydantic.main import BaseModel


class UploadFileResponse(BaseModel):
    id: str
    url: str
    success: bool

    def to_dict(self):
        return {
            'dataFileId': self.id,
            'dataFileUrl': self.url,
            'success': self.success
        }

    def __str__(self):
        data = self.to_dict()
        return str(data)
