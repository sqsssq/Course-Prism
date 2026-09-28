import { Typography } from "antd";

const { Paragraph, Title } = Typography;

export default function AboutCard() {
  return (
    <Typography>
      <Title level={4}>基本原则</Title>
      <Paragraph>本平台是独立的课程评价项目，并非港科大（广州）官方平台。</Paragraph>
      <Paragraph>请只评价自己了解的课程，描述具体经历，尊重教师与其他同学，避免发布个人隐私或无关内容。</Paragraph>
      <Paragraph>课程安排以教务系统为准。评价内容代表发布者个人观点。</Paragraph>
    </Typography>
  );
}
