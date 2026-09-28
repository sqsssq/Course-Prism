import { Card, Typography } from "antd";
import Head from "next/head";

const { Title, Paragraph } = Typography;

export default function AboutProjectPage() {
  return (
    <div style={{ maxWidth: 900, margin: "32px auto", padding: 16 }}>
      <Head><title>关于项目 - 港科大（广州）课程评价</title></Head>
      <Card>
        <Title level={2}>关于项目</Title>
        <Paragraph>这是一个独立的课程评价与选课参考项目，并非学校官方平台。课程和教学班信息同步自港科大（广州）教务系统的公开课程查询页面；评价由平台用户自行提交。</Paragraph>
        <Paragraph>课程信息可能发生变化，请以<a href="https://sisn.hkust-gz.edu.cn/cq" target="_blank" rel="noopener noreferrer">教务系统公开课程查询页</a>为准。</Paragraph>
        <Paragraph>项目基于 <a href="https://github.com/siruizou2005/Course-Prism" target="_blank" rel="noopener noreferrer">Course-Prism</a> 改造。评价内容代表发布者个人观点。</Paragraph>
      </Card>
    </div>
  );
}
