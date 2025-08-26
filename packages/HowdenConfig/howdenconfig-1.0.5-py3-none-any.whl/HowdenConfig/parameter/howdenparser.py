from pydantic import BaseModel
from HowdenConfig import Config


class Model1(BaseModel):
    provider_and_model: str = "openai:"
    path: str = "hest"

class Model2(BaseModel):
    provider_and_model: str = "llamaparser:"
    path: str = "hest2"


class Parameter(Config):
    pdf_path: str = "hest/b.json"
    split: bool = True
    llama_premium_mode: bool = True
    model1: Model1 = Model1()
    model2: Model2 = Model2()



if __name__ == "__main__":
    parameter = Parameter()




    print(parameter.model1.provider_and_model)
    print(parameter.split)
    print(parameter.pdf_path)
    print(parameter.model1.provider_and_model)
    parameter.write_to_json_file("hest.json")