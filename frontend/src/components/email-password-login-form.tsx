import { Button, Form, Input, Typography } from "antd";
import Link from "next/link";

import { EmailPasswordLoginRequest } from "@/lib/models";
import { AccountRule } from "@/lib/utils";

const EmailPasswordLoginForm = ({
  onFinish,
}: {
  onFinish: (request: EmailPasswordLoginRequest) => void;
}) => {
  const [form] = Form.useForm();

  return (
    <Form
      form={form}
      onFinish={onFinish}
      layout="horizontal"
      requiredMark="optional"
      size="large"
    >
      <Form.Item name="account" rules={[AccountRule]}>
        <Input
          id="email-password-account"
          suffix={process.env.NEXT_PUBLIC_EMAIL_ACCOUNT_DOMAIN ? `@${process.env.NEXT_PUBLIC_EMAIL_ACCOUNT_DOMAIN}` : undefined}
          placeholder="学生证号码"
        />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[{ required: true, message: "请输入选课社区密码" }]}
      >
        <Input.Password
          id="email-password"
          placeholder="选课社区密码"
          size="large"
        />
      </Form.Item>

      <Form.Item
        extra={
          <Typography.Text type="secondary">
            <Link href="/preference">忘记密码</Link>
          </Typography.Text>
        }
      >
        <Button
          type="primary"
          htmlType="submit"
          style={{ width: "100%" }}
          size="large"
        >
          使用密码登录
        </Button>
      </Form.Item>
    </Form>
  );
};

export default EmailPasswordLoginForm;
