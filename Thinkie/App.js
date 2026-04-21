import AsyncStorage from '@react-native-async-storage/async-storage';
import { StatusBar } from 'expo-status-bar';
import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

const STORAGE_KEY = 'thinkie.entries.v1';

const emotionOptions = [
  'тревога',
  'грусть',
  'злость',
  'страх',
  'стыд',
  'вина',
  'раздражение',
  'усталость',
  'одиночество',
  'другое',
];

const distortionOptions = [
  'катастрофизация',
  'чтение мыслей',
  'обесценивание хорошего',
  'черно-белое мышление',
  'долженствование',
  'сверхобобщение',
  'персонализация',
  'эмоциональное рассуждение',
];

const initialDraft = {
  situation: '',
  bodySensations: '',
  automaticThought: '',
  thoughtBelief: 50,
  emotionsBefore: [],
  distortion: '',
  evidenceFor: '',
  evidenceAgainst: '',
  alternativeExplanation: '',
  rationalAnswer: '',
  alternativeBelief: 50,
  thoughtBeliefAfter: 30,
  emotionsAfter: [],
  action: '',
};

const steps = [
  {
    eyebrow: 'Шаг 1 из 5',
    title: 'Ситуация',
    description: 'Что произошло и что откликнулось в теле?',
  },
  {
    eyebrow: 'Шаг 2 из 5',
    title: 'Автоматическая мысль',
    description: 'Та самая первая мысль, образ или воспоминание.',
  },
  {
    eyebrow: 'Шаг 3 из 5',
    title: 'Эмоции',
    description: 'Отметь эмоции и их интенсивность до разбора.',
  },
  {
    eyebrow: 'Шаг 4 из 5',
    title: 'Альтернативный ответ',
    description: 'Проверяем мысль и собираем более рациональный ответ.',
  },
  {
    eyebrow: 'Шаг 5 из 5',
    title: 'Результат',
    description: 'Что изменилось после ответа мысли?',
  },
];

export default function App() {
  const [entries, setEntries] = useState([]);
  const [screen, setScreen] = useState('home');
  const [draft, setDraft] = useState(initialDraft);
  const [step, setStep] = useState(0);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    loadEntries();
  }, []);

  async function loadEntries() {
    try {
      const savedEntries = await AsyncStorage.getItem(STORAGE_KEY);
      if (savedEntries) {
        setEntries(JSON.parse(savedEntries));
      }
    } catch (error) {
      Alert.alert('Не удалось загрузить записи', 'Попробуй открыть приложение еще раз.');
    } finally {
      setIsLoaded(true);
    }
  }

  async function persistEntries(nextEntries) {
    setEntries(nextEntries);
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(nextEntries));
  }

  function updateDraft(field, value) {
    setDraft((current) => ({ ...current, [field]: value }));
  }

  function startNewEntry() {
    setDraft(initialDraft);
    setStep(0);
    setScreen('form');
  }

  function openEntry(entry) {
    setSelectedEntry(entry);
    setScreen('details');
  }

  async function saveEntry() {
    if (!draft.situation.trim() && !draft.automaticThought.trim()) {
      Alert.alert('Добавь немного контекста', 'Заполни ситуацию или автоматическую мысль.');
      return;
    }

    const entry = {
      ...draft,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
    };

    try {
      await persistEntries([entry, ...entries]);
      setScreen('home');
      setDraft(initialDraft);
      setStep(0);
    } catch (error) {
      Alert.alert('Не удалось сохранить запись', 'Проверь, что на устройстве есть свободное место.');
    }
  }

  async function deleteEntry(id) {
    try {
      await persistEntries(entries.filter((entry) => entry.id !== id));
      setSelectedEntry(null);
      setScreen('home');
    } catch (error) {
      Alert.alert('Не удалось удалить запись', 'Попробуй еще раз.');
    }
  }

  const averageEmotionBefore = useMemo(
    () => getAverageIntensity(draft.emotionsBefore),
    [draft.emotionsBefore]
  );

  const averageEmotionAfter = useMemo(
    () => getAverageIntensity(draft.emotionsAfter),
    [draft.emotionsAfter]
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.keyboardView}
      >
        {screen === 'home' && (
          <HomeScreen
            entries={entries}
            isLoaded={isLoaded}
            onCreate={startNewEntry}
            onOpen={openEntry}
          />
        )}

        {screen === 'form' && (
          <FormScreen
            averageEmotionAfter={averageEmotionAfter}
            averageEmotionBefore={averageEmotionBefore}
            draft={draft}
            onBack={() => (step === 0 ? setScreen('home') : setStep(step - 1))}
            onCancel={() => setScreen('home')}
            onChange={updateDraft}
            onSave={saveEntry}
            setStep={setStep}
            step={step}
          />
        )}

        {screen === 'details' && selectedEntry && (
          <DetailsScreen
            entry={selectedEntry}
            onBack={() => setScreen('home')}
            onDelete={() => deleteEntry(selectedEntry.id)}
          />
        )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function HomeScreen({ entries, isLoaded, onCreate, onOpen }) {
  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.appName}>Thinkie</Text>
          <Text style={styles.subtitle}>Дневник записи мыслей</Text>
        </View>
        <Pressable accessibilityLabel="Создать запись" onPress={onCreate} style={styles.addButton}>
          <Text style={styles.addButtonText}>+</Text>
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={styles.listContent} showsVerticalScrollIndicator={false}>
        {!isLoaded && <Text style={styles.mutedText}>Загружаю записи...</Text>}

        {isLoaded && entries.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Пока нет записей</Text>
            <Text style={styles.emptyText}>
              Когда настроение изменится, нажми плюс и пройди короткую форму по шагам.
            </Text>
            <Pressable onPress={onCreate} style={styles.primaryButton}>
              <Text style={styles.primaryButtonText}>Создать первую запись</Text>
            </Pressable>
          </View>
        )}

        {entries.map((entry) => (
          <Pressable key={entry.id} onPress={() => onOpen(entry)} style={styles.entryCard}>
            <View style={styles.entryCardTop}>
              <Text style={styles.entryDate}>{formatDate(entry.createdAt)}</Text>
              <Text style={styles.entryPercent}>{entry.thoughtBeliefAfter}%</Text>
            </View>
            <Text numberOfLines={2} style={styles.entryTitle}>
              {entry.automaticThought || entry.situation || 'Запись мысли'}
            </Text>
            <Text numberOfLines={2} style={styles.entryPreview}>
              {entry.rationalAnswer || entry.action || 'Открой, чтобы посмотреть детали.'}
            </Text>
            <EmotionRow emotions={entry.emotionsAfter.length ? entry.emotionsAfter : entry.emotionsBefore} />
          </Pressable>
        ))}
      </ScrollView>
    </View>
  );
}

function FormScreen({
  averageEmotionAfter,
  averageEmotionBefore,
  draft,
  onBack,
  onCancel,
  onChange,
  onSave,
  setStep,
  step,
}) {
  const currentStep = steps[step];
  const isLastStep = step === steps.length - 1;

  return (
    <View style={styles.screen}>
      <View style={styles.formHeader}>
        <Pressable onPress={onBack} style={styles.ghostButton}>
          <Text style={styles.ghostButtonText}>Назад</Text>
        </Pressable>
        <Pressable onPress={onCancel} style={styles.ghostButton}>
          <Text style={styles.ghostButtonText}>Закрыть</Text>
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={styles.formContent} showsVerticalScrollIndicator={false}>
        <Text style={styles.eyebrow}>{currentStep.eyebrow}</Text>
        <Text style={styles.stepTitle}>{currentStep.title}</Text>
        <Text style={styles.stepDescription}>{currentStep.description}</Text>
        <ProgressDots activeStep={step} />

        {step === 0 && (
          <>
            <Field
              label="Что произошло?"
              onChangeText={(value) => onChange('situation', value)}
              placeholder="Событие, мысль, воспоминание, разговор, сон..."
              value={draft.situation}
            />
            <Field
              label="Какие ощущения были в теле?"
              onChangeText={(value) => onChange('bodySensations', value)}
              placeholder="Например: напряжение в груди, ком в горле, жар..."
              value={draft.bodySensations}
            />
          </>
        )}

        {step === 1 && (
          <>
            <Field
              label="Какая автоматическая мысль возникла?"
              onChangeText={(value) => onChange('automaticThought', value)}
              placeholder="Запиши как можно ближе к тому, как это прозвучало в голове."
              value={draft.automaticThought}
            />
            <ScaleControl
              label="Насколько я верю в эту мысль?"
              onChange={(value) => onChange('thoughtBelief', value)}
              value={draft.thoughtBelief}
            />
          </>
        )}

        {step === 2 && (
          <>
            <EmotionPicker
              emotions={draft.emotionsBefore}
              label="Какие эмоции были тогда?"
              onChange={(value) => onChange('emotionsBefore', value)}
            />
            <View style={styles.summaryStrip}>
              <Text style={styles.summaryLabel}>Средняя интенсивность</Text>
              <Text style={styles.summaryValue}>{averageEmotionBefore}%</Text>
            </View>
          </>
        )}

        {step === 3 && (
          <>
            <Text style={styles.sectionLabel}>Когнитивное искажение</Text>
            <ChipGrid
              options={distortionOptions}
              selectedValue={draft.distortion}
              onSelect={(value) => onChange('distortion', value)}
            />
            <Field
              label="Какие есть доказательства, что мысль правда?"
              onChangeText={(value) => onChange('evidenceFor', value)}
              placeholder="Факты, не ощущения."
              value={draft.evidenceFor}
            />
            <Field
              label="Какие есть доказательства против?"
              onChangeText={(value) => onChange('evidenceAgainst', value)}
              placeholder="Что не сходится или показывает другую сторону?"
              value={draft.evidenceAgainst}
            />
            <Field
              label="Есть ли альтернативное объяснение?"
              onChangeText={(value) => onChange('alternativeExplanation', value)}
              placeholder="Как еще можно понять ситуацию?"
              value={draft.alternativeExplanation}
            />
            <Field
              label="Рациональный ответ автоматической мысли"
              onChangeText={(value) => onChange('rationalAnswer', value)}
              placeholder="Что бы я сказал другу в похожей ситуации?"
              value={draft.rationalAnswer}
            />
            <ScaleControl
              label="Насколько я верю в альтернативный ответ?"
              onChange={(value) => onChange('alternativeBelief', value)}
              value={draft.alternativeBelief}
            />
          </>
        )}

        {step === 4 && (
          <>
            <ScaleControl
              label="Насколько я сейчас верю в первоначальную мысль?"
              onChange={(value) => onChange('thoughtBeliefAfter', value)}
              value={draft.thoughtBeliefAfter}
            />
            <EmotionPicker
              emotions={draft.emotionsAfter}
              label="Какие эмоции есть сейчас?"
              onChange={(value) => onChange('emotionsAfter', value)}
            />
            <View style={styles.summaryStrip}>
              <Text style={styles.summaryLabel}>Интенсивность сейчас</Text>
              <Text style={styles.summaryValue}>{averageEmotionAfter}%</Text>
            </View>
            <Field
              label="Что я сделал или сделаю?"
              onChangeText={(value) => onChange('action', value)}
              placeholder="Один следующий бережный шаг."
              value={draft.action}
            />
          </>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <Pressable
          onPress={() => (isLastStep ? onSave() : setStep(step + 1))}
          style={styles.primaryButton}
        >
          <Text style={styles.primaryButtonText}>{isLastStep ? 'Сохранить' : 'Дальше'}</Text>
        </Pressable>
      </View>
    </View>
  );
}

function DetailsScreen({ entry, onBack, onDelete }) {
  return (
    <View style={styles.screen}>
      <View style={styles.formHeader}>
        <Pressable onPress={onBack} style={styles.ghostButton}>
          <Text style={styles.ghostButtonText}>Назад</Text>
        </Pressable>
        <Pressable onPress={onDelete} style={styles.dangerButton}>
          <Text style={styles.dangerButtonText}>Удалить</Text>
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={styles.detailsContent} showsVerticalScrollIndicator={false}>
        <Text style={styles.entryDate}>{formatDate(entry.createdAt)}</Text>
        <Text style={styles.detailsTitle}>{entry.automaticThought || 'Запись мысли'}</Text>

        <DetailBlock title="Ситуация" text={entry.situation} />
        <DetailBlock title="Ощущения в теле" text={entry.bodySensations} />
        <Metric label="Вера в мысль до" value={`${entry.thoughtBelief}%`} />
        <DetailBlock title="Эмоции до" text={formatEmotions(entry.emotionsBefore)} />
        <DetailBlock title="Когнитивное искажение" text={entry.distortion} />
        <DetailBlock title="Доказательства за" text={entry.evidenceFor} />
        <DetailBlock title="Доказательства против" text={entry.evidenceAgainst} />
        <DetailBlock title="Альтернативное объяснение" text={entry.alternativeExplanation} />
        <DetailBlock title="Рациональный ответ" text={entry.rationalAnswer} />
        <Metric label="Вера в альтернативный ответ" value={`${entry.alternativeBelief}%`} />
        <Metric label="Вера в мысль после" value={`${entry.thoughtBeliefAfter}%`} />
        <DetailBlock title="Эмоции сейчас" text={formatEmotions(entry.emotionsAfter)} />
        <DetailBlock title="Действие" text={entry.action} />
      </ScrollView>
    </View>
  );
}

function Field({ label, onChangeText, placeholder, value }) {
  return (
    <View style={styles.field}>
      <Text style={styles.sectionLabel}>{label}</Text>
      <TextInput
        multiline
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor="#8d948f"
        style={styles.textInput}
        textAlignVertical="top"
        value={value}
      />
    </View>
  );
}

function ScaleControl({ label, onChange, value }) {
  const values = [0, 25, 50, 75, 100];

  return (
    <View style={styles.field}>
      <View style={styles.scaleHeader}>
        <Text style={styles.sectionLabel}>{label}</Text>
        <Text style={styles.scaleValue}>{value}%</Text>
      </View>
      <View style={styles.scaleRow}>
        {values.map((option) => (
          <Pressable
            key={option}
            onPress={() => onChange(option)}
            style={[styles.scaleOption, value === option && styles.scaleOptionActive]}
          >
            <Text style={[styles.scaleOptionText, value === option && styles.scaleOptionTextActive]}>
              {option}
            </Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

function EmotionPicker({ emotions, label, onChange }) {
  function toggleEmotion(name) {
    const exists = emotions.some((emotion) => emotion.name === name);
    if (exists) {
      onChange(emotions.filter((emotion) => emotion.name !== name));
      return;
    }
    onChange([...emotions, { name, intensity: 50 }]);
  }

  function changeIntensity(name, intensity) {
    onChange(
      emotions.map((emotion) =>
        emotion.name === name ? { ...emotion, intensity } : emotion
      )
    );
  }

  return (
    <View style={styles.field}>
      <Text style={styles.sectionLabel}>{label}</Text>
      <View style={styles.chipGrid}>
        {emotionOptions.map((option) => {
          const selected = emotions.some((emotion) => emotion.name === option);
          return (
            <Pressable
              key={option}
              onPress={() => toggleEmotion(option)}
              style={[styles.chip, selected && styles.chipActive]}
            >
              <Text style={[styles.chipText, selected && styles.chipTextActive]}>{option}</Text>
            </Pressable>
          );
        })}
      </View>

      {emotions.map((emotion) => (
        <ScaleControl
          key={emotion.name}
          label={emotion.name}
          onChange={(value) => changeIntensity(emotion.name, value)}
          value={emotion.intensity}
        />
      ))}
    </View>
  );
}

function ChipGrid({ options, selectedValue, onSelect }) {
  return (
    <View style={styles.chipGrid}>
      {options.map((option) => {
        const selected = selectedValue === option;
        return (
          <Pressable
            key={option}
            onPress={() => onSelect(selected ? '' : option)}
            style={[styles.chip, selected && styles.chipActive]}
          >
            <Text style={[styles.chipText, selected && styles.chipTextActive]}>{option}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

function ProgressDots({ activeStep }) {
  return (
    <View style={styles.progressRow}>
      {steps.map((item, index) => (
        <View
          key={item.title}
          style={[styles.progressDot, index <= activeStep && styles.progressDotActive]}
        />
      ))}
    </View>
  );
}

function EmotionRow({ emotions }) {
  if (!emotions.length) {
    return null;
  }

  return (
    <View style={styles.emotionRow}>
      {emotions.slice(0, 3).map((emotion) => (
        <Text key={emotion.name} style={styles.emotionPill}>
          {emotion.name} {emotion.intensity}%
        </Text>
      ))}
    </View>
  );
}

function DetailBlock({ title, text }) {
  if (!text) {
    return null;
  }

  return (
    <View style={styles.detailBlock}>
      <Text style={styles.detailLabel}>{title}</Text>
      <Text style={styles.detailText}>{text}</Text>
    </View>
  );
}

function Metric({ label, value }) {
  return (
    <View style={styles.metric}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
}

function getAverageIntensity(emotions) {
  if (!emotions.length) {
    return 0;
  }

  const total = emotions.reduce((sum, emotion) => sum + emotion.intensity, 0);
  return Math.round(total / emotions.length);
}

function formatEmotions(emotions) {
  if (!emotions.length) {
    return '';
  }

  return emotions.map((emotion) => `${emotion.name}: ${emotion.intensity}%`).join(', ');
}

function formatDate(value) {
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    month: 'long',
  }).format(new Date(value));
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f6f1e8',
  },
  keyboardView: {
    flex: 1,
  },
  screen: {
    flex: 1,
    backgroundColor: '#f6f1e8',
  },
  header: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 22,
  },
  appName: {
    color: '#1f2f2a',
    fontSize: 34,
    fontWeight: '800',
  },
  subtitle: {
    color: '#61716b',
    fontSize: 15,
    marginTop: 3,
  },
  addButton: {
    alignItems: 'center',
    backgroundColor: '#226b5e',
    borderRadius: 26,
    height: 52,
    justifyContent: 'center',
    width: 52,
  },
  addButtonText: {
    color: '#ffffff',
    fontSize: 32,
    lineHeight: 36,
  },
  listContent: {
    padding: 20,
    paddingBottom: 36,
  },
  mutedText: {
    color: '#61716b',
    fontSize: 16,
  },
  emptyState: {
    backgroundColor: '#ffffff',
    borderColor: '#e3ddd1',
    borderRadius: 8,
    borderWidth: 1,
    padding: 22,
  },
  emptyTitle: {
    color: '#1f2f2a',
    fontSize: 22,
    fontWeight: '800',
  },
  emptyText: {
    color: '#61716b',
    fontSize: 16,
    lineHeight: 23,
    marginTop: 10,
  },
  primaryButton: {
    alignItems: 'center',
    backgroundColor: '#226b5e',
    borderRadius: 8,
    minHeight: 52,
    justifyContent: 'center',
    marginTop: 18,
    paddingHorizontal: 18,
  },
  primaryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '800',
  },
  entryCard: {
    backgroundColor: '#ffffff',
    borderColor: '#e3ddd1',
    borderRadius: 8,
    borderWidth: 1,
    marginBottom: 12,
    padding: 16,
  },
  entryCardTop: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  entryDate: {
    color: '#61716b',
    fontSize: 13,
    fontWeight: '700',
  },
  entryPercent: {
    color: '#b05c37',
    fontSize: 14,
    fontWeight: '800',
  },
  entryTitle: {
    color: '#1f2f2a',
    fontSize: 19,
    fontWeight: '800',
    lineHeight: 24,
    marginTop: 10,
  },
  entryPreview: {
    color: '#61716b',
    fontSize: 15,
    lineHeight: 21,
    marginTop: 6,
  },
  emotionRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 12,
  },
  emotionPill: {
    backgroundColor: '#eef5f1',
    borderRadius: 8,
    color: '#226b5e',
    fontSize: 13,
    fontWeight: '700',
    overflow: 'hidden',
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  formHeader: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 14,
    paddingTop: 14,
  },
  ghostButton: {
    minHeight: 42,
    justifyContent: 'center',
    paddingHorizontal: 10,
  },
  ghostButtonText: {
    color: '#226b5e',
    fontSize: 16,
    fontWeight: '800',
  },
  dangerButton: {
    minHeight: 42,
    justifyContent: 'center',
    paddingHorizontal: 10,
  },
  dangerButtonText: {
    color: '#b23636',
    fontSize: 16,
    fontWeight: '800',
  },
  formContent: {
    padding: 20,
    paddingBottom: 110,
  },
  eyebrow: {
    color: '#b05c37',
    fontSize: 13,
    fontWeight: '900',
    textTransform: 'uppercase',
  },
  stepTitle: {
    color: '#1f2f2a',
    fontSize: 30,
    fontWeight: '900',
    marginTop: 8,
  },
  stepDescription: {
    color: '#61716b',
    fontSize: 16,
    lineHeight: 23,
    marginTop: 8,
  },
  progressRow: {
    flexDirection: 'row',
    gap: 7,
    marginBottom: 18,
    marginTop: 18,
  },
  progressDot: {
    backgroundColor: '#d8d0c3',
    borderRadius: 4,
    flex: 1,
    height: 8,
  },
  progressDotActive: {
    backgroundColor: '#226b5e',
  },
  field: {
    marginTop: 18,
  },
  sectionLabel: {
    color: '#1f2f2a',
    fontSize: 16,
    fontWeight: '800',
    lineHeight: 22,
    marginBottom: 8,
  },
  textInput: {
    backgroundColor: '#ffffff',
    borderColor: '#d9d1c4',
    borderRadius: 8,
    borderWidth: 1,
    color: '#1f2f2a',
    fontSize: 16,
    lineHeight: 22,
    minHeight: 122,
    padding: 14,
  },
  scaleHeader: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  scaleValue: {
    color: '#b05c37',
    fontSize: 18,
    fontWeight: '900',
  },
  scaleRow: {
    flexDirection: 'row',
    gap: 8,
  },
  scaleOption: {
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderColor: '#d9d1c4',
    borderRadius: 8,
    borderWidth: 1,
    flex: 1,
    minHeight: 44,
    justifyContent: 'center',
  },
  scaleOptionActive: {
    backgroundColor: '#226b5e',
    borderColor: '#226b5e',
  },
  scaleOptionText: {
    color: '#61716b',
    fontSize: 14,
    fontWeight: '800',
  },
  scaleOptionTextActive: {
    color: '#ffffff',
  },
  chipGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 9,
  },
  chip: {
    backgroundColor: '#ffffff',
    borderColor: '#d9d1c4',
    borderRadius: 8,
    borderWidth: 1,
    minHeight: 42,
    justifyContent: 'center',
    paddingHorizontal: 12,
    paddingVertical: 9,
  },
  chipActive: {
    backgroundColor: '#e5f1ec',
    borderColor: '#226b5e',
  },
  chipText: {
    color: '#42524d',
    fontSize: 14,
    fontWeight: '700',
  },
  chipTextActive: {
    color: '#226b5e',
  },
  summaryStrip: {
    alignItems: 'center',
    backgroundColor: '#fff7e8',
    borderColor: '#eadab7',
    borderRadius: 8,
    borderWidth: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 18,
    padding: 14,
  },
  summaryLabel: {
    color: '#735837',
    fontSize: 15,
    fontWeight: '800',
  },
  summaryValue: {
    color: '#b05c37',
    fontSize: 20,
    fontWeight: '900',
  },
  footer: {
    backgroundColor: '#f6f1e8',
    borderColor: '#e3ddd1',
    borderTopWidth: 1,
    bottom: 0,
    left: 0,
    padding: 16,
    position: 'absolute',
    right: 0,
  },
  detailsContent: {
    padding: 20,
    paddingBottom: 40,
  },
  detailsTitle: {
    color: '#1f2f2a',
    fontSize: 28,
    fontWeight: '900',
    lineHeight: 34,
    marginTop: 8,
  },
  detailBlock: {
    backgroundColor: '#ffffff',
    borderColor: '#e3ddd1',
    borderRadius: 8,
    borderWidth: 1,
    marginTop: 12,
    padding: 14,
  },
  detailLabel: {
    color: '#61716b',
    fontSize: 13,
    fontWeight: '900',
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  detailText: {
    color: '#1f2f2a',
    fontSize: 16,
    lineHeight: 23,
  },
  metric: {
    alignItems: 'center',
    backgroundColor: '#eef5f1',
    borderColor: '#cfe3d9',
    borderRadius: 8,
    borderWidth: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    padding: 14,
  },
  metricLabel: {
    color: '#226b5e',
    flex: 1,
    fontSize: 15,
    fontWeight: '800',
  },
  metricValue: {
    color: '#226b5e',
    fontSize: 20,
    fontWeight: '900',
    marginLeft: 12,
  },
});
