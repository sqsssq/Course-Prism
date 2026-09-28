import { Card, Typography } from "antd";
import Head from "next/head";
import Link from "next/link";

const { Paragraph, Title } = Typography;

export default function SyncPage() {
  return (
    <Card style={{ maxWidth: 720, margin: "32px auto" }}>
      <Head><title>课表同步 - 港科大（广州）课程评价</title></Head>
      <Title level={3}>课表同步尚未开放</Title>
      <Paragraph>目前可在课程库搜索课程，并选择实际修读学期提交评价。课表同步将在后续版本添加。</Paragraph>
      <Link href="/courses">浏览课程库</Link>
    </Card>
  );
}
