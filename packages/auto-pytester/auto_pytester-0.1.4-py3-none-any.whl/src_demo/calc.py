
class Calc:

    @classmethod
    def add(cls, a: int, b: int) -> int:
        """
        加法

        Examples:
            >>> yaml
            doc: "expect 2 + 3 == 5"
            input:
              a: 2
              b: 3
            output:
              5
            <<<
            >>> json
            {
              "doc": "expect 33 + 3 == 102",
              "input": {"a":99,"b":3},
              "output": 102
            }
            <<<
            >>> toml
            [input]
            a = 9
            b = 3
            [output]
            value = 12
            <<<
        """
        return a + b

    @classmethod
    def div(cls, a: int, b: int) -> float:
        """
        除法

        Examples:
            >>> yaml
            input:
              a: 6
              b: 3
            output:
              2
            <<<
        """
        if b == 0:
            raise ValueError("divide by zero")
        return a / b


if __name__ == "__main__":
    import requests
    import json

    url = "http://192.168.20.58/radiusapi/collect_patient_info/"
    payload = {"patientId": "13193650", "name": "刘明珠"}
    headers = {"Content-Type": "application/json"}

    # allow_redirects=False 禁止自动跟随重定向，马上能看出有没有 301/302
    resp = requests.post(
        url, data=json.dumps(payload), headers=headers, allow_redirects=False
    )

    print("HTTP 状态码 :", resp.status_code)
    print("响应头     :", dict(resp.headers))
    print("响应正文   :", resp.text)
