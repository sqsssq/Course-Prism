import { Card, Typography } from "antd";
import Head from "next/head";

const { Title, Paragraph } = Typography;

export default function FaqPage() {
  return (
    <div style={{ maxWidth: 900, margin: "32px auto", padding: 16 }}>
      <Head><title>常见问题 - 港科大（广州）课程评价</title></Head>
      <Card>
        <Title level={2}>常见问题</Title>
        <Title level={4}>课程信息从哪里来？</Title>
        <Paragraph>课程与教学班信息来自教务系统的公开课程查询页面，按学期同步。具体安排请以教务系统为准。</Paragraph>
        <Title level={4}>谁可以写评价？</Title>
        <Paragraph>拥有平台账户的用户可以评价课程。请只评价自己了解的课程，并描述具体体验。</Paragraph>
        <Title level={4}>这是学校官方平台吗？</Title>
        <Paragraph>不是。本项目由独立开发者维护，课程评价也不代表学校立场。</Paragraph>
      </Card>
    </div>
  );
}
