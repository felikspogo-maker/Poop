import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Starting database seeding...');

  // Clear existing data
  console.log('🧹 Cleaning up existing data...');
  await prisma.message.deleteMany();
  await prisma.conversation.deleteMany();
  await prisma.document.deleteMany();
  await prisma.payment.deleteMany();
  await prisma.consultation.deleteMany();
  await prisma.consultant.deleteMany();
  await prisma.user.deleteMany();

  // Create password hash
  const hashedPassword = await bcrypt.hash('password123', 10);

  // Create test clients
  console.log('👥 Creating test clients...');
  const client1 = await prisma.user.create({
    data: {
      email: 'client1@example.com',
      password: hashedPassword,
      firstName: 'Иван',
      lastName: 'Петров',
      phone: '+79001234567',
      role: 'CLIENT',
    },
  });

  const client2 = await prisma.user.create({
    data: {
      email: 'client2@example.com',
      password: hashedPassword,
      firstName: 'Мария',
      lastName: 'Сидорова',
      phone: '+79001234568',
      role: 'CLIENT',
    },
  });

  const client3 = await prisma.user.create({
    data: {
      email: 'client3@example.com',
      password: hashedPassword,
      firstName: 'Алексей',
      lastName: 'Смирнов',
      phone: '+79001234569',
      role: 'CLIENT',
    },
  });

  // Create test consultants
  console.log('👨‍💼 Creating test consultants...');
  const consultantUser1 = await prisma.user.create({
    data: {
      email: 'consultant1@example.com',
      password: hashedPassword,
      firstName: 'Дмитрий',
      lastName: 'Козлов',
      phone: '+79007654321',
      role: 'CONSULTANT',
    },
  });

  const consultant1 = await prisma.consultant.create({
    data: {
      userId: consultantUser1.id,
      specialization: 'Финансы',
      bio: 'Опытный финансовый консультант с 10+ летним стажем. Специализируюсь на инвестициях, налоговом планировании и финансовой оптимизации бизнеса.',
      hourlyRate: 5000,
      rating: 4.8,
      reviewsCount: 127,
      skills: ['Финансовый анализ', 'Инвестиции', 'Налоги', 'Бюджетирование'],
    },
  });

  const consultantUser2 = await prisma.user.create({
    data: {
      email: 'consultant2@example.com',
      password: hashedPassword,
      firstName: 'Елена',
      lastName: 'Волкова',
      phone: '+79007654322',
      role: 'CONSULTANT',
    },
  });

  const consultant2 = await prisma.consultant.create({
    data: {
      userId: consultantUser2.id,
      specialization: 'Маркетинг',
      bio: 'Эксперт по digital-маркетингу и продвижению бренда. Помогу вывести ваш бизнес на новый уровень с помощью современных маркетинговых стратегий.',
      hourlyRate: 4500,
      rating: 4.9,
      reviewsCount: 95,
      skills: ['Digital маркетинг', 'SMM', 'SEO', 'Контент-стратегия', 'Аналитика'],
    },
  });

  const consultantUser3 = await prisma.user.create({
    data: {
      email: 'consultant3@example.com',
      password: hashedPassword,
      firstName: 'Андрей',
      lastName: 'Морозов',
      phone: '+79007654323',
      role: 'CONSULTANT',
    },
  });

  const consultant3 = await prisma.consultant.create({
    data: {
      userId: consultantUser3.id,
      specialization: 'HR',
      bio: 'HR-консультант и бизнес-коуч. Специализируюсь на построении эффективных команд, корпоративной культуре и развитии персонала.',
      hourlyRate: 4000,
      rating: 4.7,
      reviewsCount: 73,
      skills: ['Рекрутинг', 'Корпоративная культура', 'Обучение', 'Team building'],
    },
  });

  const consultantUser4 = await prisma.user.create({
    data: {
      email: 'consultant4@example.com',
      password: hashedPassword,
      firstName: 'Ольга',
      lastName: 'Новикова',
      phone: '+79007654324',
      role: 'CONSULTANT',
    },
  });

  const consultant4 = await prisma.consultant.create({
    data: {
      userId: consultantUser4.id,
      specialization: 'IT',
      bio: 'IT-консультант и архитектор решений. Помогу с цифровой трансформацией вашего бизнеса, выбором технологий и автоматизацией процессов.',
      hourlyRate: 6000,
      rating: 5.0,
      reviewsCount: 45,
      skills: ['Цифровая трансформация', 'Cloud решения', 'DevOps', 'Автоматизация'],
    },
  });

  const consultantUser5 = await prisma.user.create({
    data: {
      email: 'consultant5@example.com',
      password: hashedPassword,
      firstName: 'Сергей',
      lastName: 'Лебедев',
      phone: '+79007654325',
      role: 'CONSULTANT',
    },
  });

  const consultant5 = await prisma.consultant.create({
    data: {
      userId: consultantUser5.id,
      specialization: 'Стратегия',
      bio: 'Стратегический консультант с MBA. Разработаю стратегию развития вашего бизнеса, помогу с масштабированием и выходом на новые рынки.',
      hourlyRate: 7000,
      rating: 4.9,
      reviewsCount: 62,
      skills: ['Бизнес-стратегия', 'Масштабирование', 'Анализ рынка', 'Конкурентный анализ'],
    },
  });

  const consultantUser6 = await prisma.user.create({
    data: {
      email: 'consultant6@example.com',
      password: hashedPassword,
      firstName: 'Татьяна',
      lastName: 'Соколова',
      phone: '+79007654326',
      role: 'CONSULTANT',
    },
  });

  const consultant6 = await prisma.consultant.create({
    data: {
      userId: consultantUser6.id,
      specialization: 'Юридические',
      bio: 'Юрист-консультант по корпоративному праву. Помогу с юридической структурой бизнеса, договорами и правовыми вопросами.',
      hourlyRate: 5500,
      rating: 4.8,
      reviewsCount: 88,
      skills: ['Корпоративное право', 'Договоры', 'Налоговое право', 'IP защита'],
    },
  });

  // Create test consultations
  console.log('📅 Creating test consultations...');
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(10, 0, 0, 0);

  const nextWeek = new Date(now);
  nextWeek.setDate(nextWeek.getDate() + 7);
  nextWeek.setHours(14, 0, 0, 0);

  const consultation1 = await prisma.consultation.create({
    data: {
      userId: client1.id,
      consultantId: consultant1.id,
      date: tomorrow,
      duration: 60,
      description: 'Консультация по финансовому планированию для стартапа',
      status: 'SCHEDULED',
    },
  });

  const consultation2 = await prisma.consultation.create({
    data: {
      userId: client1.id,
      consultantId: consultant2.id,
      date: nextWeek,
      duration: 90,
      description: 'Разработка маркетинговой стратегии',
      status: 'SCHEDULED',
    },
  });

  const pastDate = new Date(now);
  pastDate.setDate(pastDate.getDate() - 7);

  await prisma.consultation.create({
    data: {
      userId: client2.id,
      consultantId: consultant3.id,
      date: pastDate,
      duration: 60,
      description: 'Консультация по найму персонала',
      status: 'COMPLETED',
    },
  });

  // Create conversations
  console.log('💬 Creating test conversations...');
  const conversation1 = await prisma.conversation.create({
    data: {
      participants: {
        connect: [{ id: client1.id }, { id: consultantUser1.id }],
      },
    },
  });

  // Create messages
  await prisma.message.createMany({
    data: [
      {
        conversationId: conversation1.id,
        senderId: client1.id,
        receiverId: consultantUser1.id,
        content: 'Здравствуйте! Хочу проконсультироваться по вопросам инвестирования.',
        read: true,
        createdAt: new Date(now.getTime() - 3600000),
      },
      {
        conversationId: conversation1.id,
        senderId: consultantUser1.id,
        receiverId: client1.id,
        content: 'Добрый день! Конечно, буду рад помочь. Какой у вас инвестиционный горизонт?',
        read: true,
        createdAt: new Date(now.getTime() - 3000000),
      },
      {
        conversationId: conversation1.id,
        senderId: client1.id,
        receiverId: consultantUser1.id,
        content: 'Планирую инвестировать на 3-5 лет. Интересуют надежные инструменты.',
        read: false,
        createdAt: new Date(now.getTime() - 1800000),
      },
    ],
  });

  console.log('✅ Database seeding completed successfully!');
  console.log('\n📊 Created:');
  console.log('  - 3 test clients');
  console.log('  - 6 test consultants');
  console.log('  - 3 test consultations');
  console.log('  - 1 conversation with messages');
  console.log('\n🔑 Test credentials:');
  console.log('  Client: client1@example.com / password123');
  console.log('  Consultant: consultant1@example.com / password123');
  console.log('  (All users have the same password: password123)');
}

main()
  .catch((e) => {
    console.error('❌ Error seeding database:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
