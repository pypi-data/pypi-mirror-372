import re

class CalculatorMCPService:
    """简单计算器MCP服务类，支持加、减、乘、除四则运算"""
    
    def __init__(self):
        # 初始化计算器服务
        pass
        
    def parse_expression(self, expression):
        """解析数学表达式，提取操作数和运算符"""
        # 移除表达式中的空格
        expression = expression.replace(" ", "")
        
        # 匹配加减乘除运算符
        match = re.search(r'([\+\-\*\/])', expression)
        if not match:
            return None, None, None
        
        operator = match.group(1)
        # 分割操作数
        try:
            num1 = float(expression[:match.start()])
            num2 = float(expression[match.end():])
            return num1, operator, num2
        except ValueError:
            return None, None, None
    
    def calculate(self, expression):
        """计算数学表达式的结果"""
        num1, operator, num2 = self.parse_expression(expression)
        
        if num1 is None or num2 is None:
            return "错误：无效的表达式格式"
        
        try:
            if operator == '+':
                return f"计算结果：{num1 + num2}"
            elif operator == '-':
                return f"计算结果：{num1 - num2}"
            elif operator == '*':
                return f"计算结果：{num1 * num2}"
            elif operator == '/':
                if num2 == 0:
                    return "错误：除数不能为零"
                return f"计算结果：{num1 / num2}"
            else:
                return "错误：不支持的运算符"
        except Exception as e:
            return f"计算错误：{str(e)}"
    
    def run_service(self):
        """运行MCP服务的主函数"""
        print("计算器MCP服务已启动")
        print("支持的运算：加(+), 减(-), 乘(*), 除(/)")
        print("请输入表达式（例如：2+3），输入'q'退出")
        
        while True:
            try:
                user_input = input("请输入表达式: ")
                
                if user_input.lower() == 'q':
                    print("计算器MCP服务已停止")
                    break
                
                result = self.calculate(user_input)
                print(result)
            except KeyboardInterrupt:
                print("\n计算器MCP服务已停止")
                break

# 添加main函数以便作为命令行工具运行
def main():
    calculator_service = CalculatorMCPService()
    calculator_service.run_service()

if __name__ == "__main__":
    main()