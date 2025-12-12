// frontend/App.js
import * as React from 'react';
import { useState, useMemo, useEffect, useRef } from 'react';
import dayjs from 'dayjs';
import { DateCalendar } from '@mui/x-date-pickers/DateCalendar';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Box,
  Typography,
  Switch,
  Stack,
  Toolbar,
  AppBar,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Paper,
  Divider,
  TextField,
  InputAdornment,
  Button,
  CircularProgress,
  Badge,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormGroup,
  FormControlLabel,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  Snackbar,
  Tooltip,
  Avatar,
  ListItemAvatar,
  ListItemSecondaryAction,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  LightMode, DarkMode, Menu as MenuIcon, Send as SendIcon,
  Mic as MicIcon, MicOff as MicOffIcon, Sync as SyncIcon,
  Google as GoogleIcon, Email as EmailIcon, Notifications as NotificationsIcon,
  CloudUpload as CloudUploadIcon, CloudDone as CloudDoneIcon,
  Event as EventIcon, Schedule as ScheduleIcon, LocationOn as LocationIcon,
  Group as GroupIcon, PriorityHigh as PriorityIcon, Category as CategoryIcon,
  MoreVert as MoreIcon, CheckCircle as CheckCircleIcon,
  Error as ErrorIcon, Warning as WarningIcon, Info as InfoIcon,
  Refresh as RefreshIcon, Delete as DeleteIcon, Edit as EditIcon,
  Add as AddIcon, VoiceOverOff as VoiceOverOffIcon
} from '@mui/icons-material';

// --- Configuration ---
const AGENT_API_URL = "http://localhost:8001/chat";
const MCP_API_URL = "http://localhost:8000";
const VOICE_API_URL = "http://localhost:8003/voice/process";

// --- Theme Definition ---
const getAppTheme = (mode) =>
  createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'dark' ? '#90caf9' : '#1976d2',
      },
      secondary: {
        main: mode === 'dark' ? '#f48fb1' : '#dc004e',
      },
      success: {
        main: mode === 'dark' ? '#66bb6a' : '#4caf50',
      },
      warning: {
        main: mode === 'dark' ? '#ffb74d' : '#ff9800',
      },
      error: {
        main: mode === 'dark' ? '#f44336' : '#d32f2f',
      },
      info: {
        main: mode === 'dark' ? '#29b6f6' : '#0288d1',
      },
      background: {
        default: mode === 'dark' ? '#121212' : '#f5f5f5',
        paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
      },
    },
    typography: {
      fontFamily: [
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
      ].join(','),
    },
  });

// --- Event Creation Dialog ---
function EventCreationDialog({ open, onClose, onSave, defaultDate }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [startTime, setStartTime] = useState(dayjs(defaultDate).hour(9).minute(0).format('YYYY-MM-DDTHH:mm'));
  const [endTime, setEndTime] = useState(dayjs(defaultDate).hour(10).minute(0).format('YYYY-MM-DDTHH:mm'));
  const [attendees, setAttendees] = useState('');
  const [priority, setPriority] = useState('medium');
  const [category, setCategory] = useState('');
  const [syncToGoogle, setSyncToGoogle] = useState(false);
  const [sendInvites, setSendInvites] = useState(false);
  const [reminders, setReminders] = useState([30, 60]); // minutes before

  const handleSave = () => {
    const eventData = {
      title,
      description,
      location,
      start_time: dayjs(startTime).toISOString(),
      end_time: dayjs(endTime).toISOString(),
      attendees: attendees.split(',').map(email => email.trim()).filter(email => email),
      priority,
      category,
      sync_to_google: syncToGoogle,
      send_invites: sendInvites,
      reminders: reminders.map(minutes => ({ method: 'email', minutes }))
    };
    onSave(eventData);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create New Event</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 2 }}>
          <TextField
            label="Event Title"
            fullWidth
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <TextField
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <Stack direction="row" spacing={2}>
            <TextField
              label="Start Time"
              type="datetime-local"
              fullWidth
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="End Time"
              type="datetime-local"
              fullWidth
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Stack>
          <TextField
            label="Location"
            fullWidth
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
          <TextField
            label="Attendees (comma-separated emails)"
            fullWidth
            value={attendees}
            onChange={(e) => setAttendees(e.target.value)}
            placeholder="user1@example.com, user2@example.com"
          />
          <Stack direction="row" spacing={2}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={priority}
                label="Priority"
                onChange={(e) => setPriority(e.target.value)}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Category"
              fullWidth
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
          </Stack>
          <FormGroup>
            <FormControlLabel
              control={<Checkbox checked={syncToGoogle} onChange={(e) => setSyncToGoogle(e.target.checked)} />}
              label="Sync to Google Calendar"
            />
            <FormControlLabel
              control={<Checkbox checked={sendInvites} onChange={(e) => setSendInvites(e.target.checked)} />}
              label="Send email invites to attendees"
              disabled={!attendees}
            />
          </FormGroup>
          <FormControl fullWidth>
            <InputLabel>Reminders</InputLabel>
            <Select
              multiple
              value={reminders}
              onChange={(e) => setReminders(e.target.value)}
              renderValue={(selected) => selected.map(m => `${m} min`).join(', ')}
            >
              {[5, 15, 30, 60, 120, 1440].map((minutes) => (
                <MenuItem key={minutes} value={minutes}>
                  {minutes} minutes before
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" color="primary" disabled={!title}>
          Create Event
        </Button>
      </DialogActions>
    </Dialog>
  );
}

// --- Main App Component ---
export default function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [selectedDate, setSelectedDate] = useState(dayjs());
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showEventDialog, setShowEventDialog] = useState(false);
  const [events, setEvents] = useState([]);
  const [syncStatus, setSyncStatus] = useState({});
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [voiceRecognition, setVoiceRecognition] = useState(null);
  const [isGoogleConnected, setIsGoogleConnected] = useState(false);
  
  const [chatMessages, setChatMessages] = useState([
    { id: 1, text: "Hello! I'm your enhanced AI Calendar Assistant. I can help you create events, sync with Google Calendar, send email reminders, and understand voice commands!", sender: 'ai' },
    { id: 2, text: "Try saying: 'Schedule a team meeting tomorrow at 3 PM and sync it to Google Calendar'", sender: 'ai' },
  ]);

  const theme = useMemo(() => getAppTheme(darkMode ? 'dark' : 'light'), [darkMode]);

  // Refs
  const chatEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize voice recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
        handleVoiceCommand(transcript);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        showSnackbar('Voice recognition error: ' + event.error, 'error');
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      setVoiceRecognition(recognition);
    } else {
      console.warn('Speech recognition not supported');
      showSnackbar('Voice recognition is not supported in your browser', 'warning');
    }
  }, []);

  // Check Google connection status
  useEffect(() => {
    checkGoogleConnection();
    fetchEvents();
  }, []);

  const checkGoogleConnection = async () => {
    try {
      const response = await fetch(`${MCP_API_URL}/auth/google/url`);
      if (response.ok) {
        setIsGoogleConnected(true);
      }
    } catch (error) {
      console.log('Google Calendar not configured');
    }
  };

  const fetchEvents = async () => {
    try {
      const response = await fetch(`${MCP_API_URL}/events`);
      if (response.ok) {
        const data = await response.json();
        setEvents(data);
      }
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  // --- NEW: Helper to call TTS microservice and play audio ---
  const playVoiceResponse = async (text) => {
    try {
      if (!text || !VOICE_API_URL) return;

      const response = await fetch(VOICE_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // accept NDJSON stream; backend uses StreamingResponse with application/x-ndjson
          'Accept': 'application/x-ndjson'
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok || !response.body) {
        console.error('TTS request failed:', response.status, response.statusText);
        showSnackbar('Failed to generate voice response', 'error');
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let partial = '';
      const audioChunks = [];

      // Read NDJSON stream line by line, collect base64 audio fragments
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        partial += decoder.decode(value, { stream: true });

        const lines = partial.split('\n');
        partial = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          try {
            const obj = JSON.parse(trimmed);
            const b64 = obj.audio_base64 || obj.audio || null;
            if (b64) {
              audioChunks.push(b64);
            }
          } catch (err) {
            console.warn('Failed to parse NDJSON line from TTS:', err, line);
          }
        }
      }

      if (audioChunks.length === 0) {
        console.warn('No audio chunks received from TTS');
        return;
      }

      // Concatenate base64 audio chunks and play as WAV
      const base64Audio = audioChunks.join('');
      const byteChars = atob(base64Audio);
      const byteNumbers = new Array(byteChars.length);
      for (let i = 0; i < byteChars.length; i++) {
        byteNumbers[i] = byteChars.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);

      const audio = new Audio(url);
      audio.onended = () => URL.revokeObjectURL(url);
      audio.play().catch((err) => {
        console.error('Error playing TTS audio:', err);
      });
    } catch (error) {
      console.error('TTS error:', error);
      showSnackbar('Error during voice playback', 'error');
    }
  };

  const handleVoiceCommand = async (transcript) => {
    // Add user voice message
    const userMessage = { id: Date.now(), text: `🎤 ${transcript}`, sender: 'user' };
    setChatMessages(prev => [...prev, userMessage]);
    
    // Send to AI agent and request spoken reply
    await sendMessageToAgent(transcript, true);
  };

  const startVoiceRecognition = () => {
    if (voiceRecognition && !isListening) {
      voiceRecognition.start();
      setIsListening(true);
      showSnackbar('Listening... Speak now', 'info');
    }
  };

  const stopVoiceRecognition = () => {
    if (voiceRecognition && isListening) {
      voiceRecognition.stop();
      setIsListening(false);
    }
  };

  const handleImportGoogle = async () => {
    try {
      showSnackbar('Importing events from Google Calendar...', 'info');
      const response = await fetch(`${MCP_API_URL}/events/import/google`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.status === 'success') {
        showSnackbar(`Imported ${data.count} events from Google Calendar`, 'success');
        fetchEvents();
        // Add AI message about import
        setChatMessages(prev => [...prev, {
          id: Date.now(),
          text: `✅ Imported ${data.count} events from Google Calendar. I've added them to your local calendar.`,
          sender: 'ai'
        }]);
      } else {
        showSnackbar('Failed to import from Google: ' + data.message, 'error');
      }
    } catch (error) {
      showSnackbar('Failed to connect to Google Calendar', 'error');
    }
  };

  const handleSyncEvent = async (eventId) => {
    try {
      showSnackbar('Syncing event to Google Calendar...', 'info');
      const response = await fetch(`${MCP_API_URL}/events/${eventId}/sync`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.status === 'success') {
        showSnackbar('Event synced to Google Calendar', 'success');
        fetchEvents();
      } else {
        showSnackbar('Sync failed: ' + data.message, 'error');
      }
    } catch (error) {
      showSnackbar('Sync failed', 'error');
    }
  };

  const handleSendReminder = async (eventId) => {
    try {
      showSnackbar('Sending reminder...', 'info');
      const response = await fetch(`${MCP_API_URL}/mcp/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: "send_event_reminder_tool",
          tool_args: { event_id: eventId }
        })
      });
      const data = await response.json();
      if (data.result?.status === 'success') {
        showSnackbar('Reminder sent successfully', 'success');
      } else {
        showSnackbar('Failed to send reminder', 'error');
      }
    } catch (error) {
      showSnackbar('Failed to send reminder', 'error');
    }
  };

  // --- UPDATED: speak flag controls whether we call TTS ---
  const sendMessageToAgent = async (message, speak = false) => {
    setIsSending(true);
    
    try {
      const response = await fetch(AGENT_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      const aiText = data.response || "Sorry, I received an empty response.";
      const aiMessage = { 
        id: Date.now() + 1, 
        text: aiText, 
        sender: 'ai' 
      };
      setChatMessages(prev => [...prev, aiMessage]);

      // Refresh events after agent action
      fetchEvents();

      // If this came from a voice command, speak the AI response
      if (speak) {
        await playVoiceResponse(aiText);
      }
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = { 
        id: Date.now() + 1, 
        text: `Error: ${error.message}`, 
        sender: 'error' 
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const handleSendMessage = () => {
    const message = inputMessage.trim();
    if (!message || isSending) return;

    const userMessage = { id: Date.now(), text: message, sender: 'user' };
    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    
    // Text input: do NOT speak by default
    sendMessageToAgent(message, false);
  };

  const handleSaveEvent = async (eventData) => {
    try {
      const response = await fetch(`${MCP_API_URL}/mcp/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: "create_calendar_event_tool",
          tool_args: eventData
        })
      });
      
      const data = await response.json();
      if (data.result?.status === 'success') {
        showSnackbar('Event created successfully', 'success');
        fetchEvents();
        
        // Add AI confirmation
        setChatMessages(prev => [...prev, {
          id: Date.now(),
          text: `✅ Created event "${eventData.title}"${eventData.sync_to_google ? ' and synced to Google Calendar' : ''}.`,
          sender: 'ai'
        }]);
      } else {
        showSnackbar('Failed to create event: ' + data.result?.message, 'error');
      }
    } catch (error) {
      showSnackbar('Failed to create event', 'error');
    }
  };

  // Get events for selected date
  const filteredEvents = events.filter(event => {
    const eventDate = dayjs(event.start_time).format('YYYY-MM-DD');
    const selectedDateStr = selectedDate.format('YYYY-MM-DD');
    return eventDate === selectedDateStr;
  });

  // Scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Speed dial actions
  const speedDialActions = [
    { icon: <AddIcon />, name: 'New Event', action: () => setShowEventDialog(true) },
    { icon: <SyncIcon />, name: 'Sync All', action: () => showSnackbar('Syncing all events...', 'info') },
    { icon: <EmailIcon />, name: 'Send Reminders', action: () => showSnackbar('Sending all reminders...', 'info') },
    { icon: <GoogleIcon />, name: 'Import Google', action: handleImportGoogle },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      
      {/* App Bar with enhanced features */}
      <AppBar position="static" color="primary">
        <Toolbar>
          <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Calendar Pro+
          </Typography>
          
          {/* Google Import Button */}
          <Tooltip title={isGoogleConnected ? "Import from Google Calendar" : "Connect Google Calendar first"}>
            <span>
              <IconButton 
                color="inherit" 
                onClick={handleImportGoogle}
                disabled={!isGoogleConnected}
                sx={{ mr: 2 }}
              >
                <GoogleIcon />
              </IconButton>
            </span>
          </Tooltip>
          
          {/* Sync Status Badge */}
          <Chip 
            icon={<SyncIcon />}
            label={`${events.filter(e => e.synced).length}/${events.length} synced`}
            color={events.filter(e => e.synced).length === events.length ? "success" : "default"}
            variant="outlined"
            sx={{ mr: 2, color: 'white' }}
          />
          
          {/* Dark Mode Switch */}
          <Stack direction="row" spacing={1} alignItems="center">
            <LightMode />
            <Switch
              checked={darkMode}
              onChange={() => setDarkMode(!darkMode)}
              name="darkModeToggle"
              inputProps={{ 'aria-label': 'toggle dark mode' }}
            />
            <DarkMode />
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ pt: 4, pb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>

        {/* Stats Cards */}
        <Stack direction="row" spacing={2} sx={{ mb: 4 }}>
          <Paper sx={{ p: 2, flex: 1, display: 'flex', alignItems: 'center' }}>
            <EventIcon color="primary" sx={{ mr: 2 }} />
            <Box>
              <Typography variant="h6">{events.length}</Typography>
              <Typography variant="body2" color="textSecondary">Total Events</Typography>
            </Box>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, display: 'flex', alignItems: 'center' }}>
            <CloudDoneIcon color="success" sx={{ mr: 2 }} />
            <Box>
              <Typography variant="h6">{events.filter(e => e.synced).length}</Typography>
              <Typography variant="body2" color="textSecondary">Synced</Typography>
            </Box>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, display: 'flex', alignItems: 'center' }}>
            <NotificationsIcon color="warning" sx={{ mr: 2 }} />
            <Box>
              <Typography variant="h6">{events.filter(e => e.reminders?.length > 0).length}</Typography>
              <Typography variant="body2" color="textSecondary">With Reminders</Typography>
            </Box>
          </Paper>
        </Stack>

        {/* Calendar and Chat Layout */}
        <Stack
          direction={{ xs: 'column', lg: 'row' }}
          spacing={4}
          mt={2}
          alignItems="flex-start"
        >
          {/* Calendar Panel */}
          <Paper elevation={3} sx={{ flex: 1, minWidth: 350, p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h5">Calendar View</Typography>
              <Button 
                variant="outlined" 
                startIcon={<AddIcon />}
                onClick={() => setShowEventDialog(true)}
              >
                New Event
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DateCalendar
                value={selectedDate}
                onChange={setSelectedDate}
                sx={{ width: '100%' }}
              />
            </LocalizationProvider>
            
            {/* Events for selected date */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Events for {selectedDate.format('MMMM D, YYYY')}
              </Typography>
              {filteredEvents.length === 0 ? (
                <Typography color="textSecondary" align="center" sx={{ py: 4 }}>
                  No events scheduled
                </Typography>
              ) : (
                <List>
                  {filteredEvents.map((event) => (
                    <ListItem 
                      key={event.id}
                      secondaryAction={
                        <Stack direction="row" spacing={1}>
                          <Tooltip title="Sync to Google">
                            <IconButton 
                              edge="end" 
                              size="small"
                              onClick={() => handleSyncEvent(event.id)}
                              disabled={event.synced}
                            >
                              {event.synced ? <CloudDoneIcon color="success" /> : <SyncIcon />}
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Send Reminder">
                            <IconButton 
                              edge="end" 
                              size="small"
                              onClick={() => handleSendReminder(event.id)}
                            >
                              <EmailIcon />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      }
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: event.priority === 'high' ? 'error.main' : 
                                           event.priority === 'medium' ? 'warning.main' : 'info.main' }}>
                          {event.title.charAt(0)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="subtitle1">{event.title}</Typography>
                            {event.synced && (
                              <Chip 
                                size="small" 
                                label="Synced" 
                                color="success" 
                                sx={{ ml: 1 }}
                                icon={<CloudDoneIcon />}
                              />
                            )}
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography variant="body2" color="textSecondary">
                              {dayjs(event.start_time).format('h:mm A')} - {dayjs(event.end_time).format('h:mm A')}
                            </Typography>
                            {event.location && (
                              <Typography variant="body2" color="textSecondary">
                                <LocationIcon sx={{ fontSize: 12, verticalAlign: 'middle', mr: 0.5 }} />
                                {event.location}
                              </Typography>
                            )}
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          </Paper>

          {/* Chat Panel */}
          <Paper elevation={3} sx={{ flex: 1, minWidth: 400, display: 'flex', flexDirection: 'column', height: 700 }}>
            <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h5">AI Assistant Chat</Typography>
              <Box>
                <Tooltip title={isListening ? "Stop listening" : "Voice command"}>
                  <IconButton 
                    color={isListening ? "error" : "primary"}
                    onClick={isListening ? stopVoiceRecognition : startVoiceRecognition}
                    sx={{ mr: 1 }}
                  >
                    {isListening ? <MicOffIcon /> : <MicIcon />}
                  </IconButton>
                </Tooltip>
                {isListening && (
                  <CircularProgress size={24} color="error" sx={{ animation: 'pulse 1s infinite' }} />
                )}
              </Box>
            </Box>

            {/* Message List */}
            <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
              <List>
                {chatMessages.map((message) => (
                  <ListItem 
                    key={message.id}
                    sx={{ 
                      justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                      width: '100%', 
                      py: 0.5
                    }}
                  >
                    <Paper 
                      variant="outlined" 
                      sx={{
                        p: 1.5,
                        maxWidth: '85%',
                        borderRadius: '20px',
                        backgroundColor: message.sender === 'user' 
                          ? theme.palette.primary.main 
                          : message.sender === 'ai'
                          ? theme.palette.background.default
                          : theme.palette.error.dark,
                        color: message.sender === 'user' ? 'white' : 'inherit',
                      }}
                    >
                      <ListItemText 
                        primary={message.text} 
                        sx={{ m: 0, whiteSpace: 'pre-wrap' }} 
                      />
                    </Paper>
                  </ListItem>
                ))}
                <div ref={chatEndRef} />
              </List>
              
              {isSending && (
                <Stack direction="row" spacing={1} sx={{ mt: 1, justifyContent: 'flex-start' }}>
                  <CircularProgress size={20} color="primary" />
                  <Typography variant="body2" color="textSecondary">AI is thinking...</Typography>
                </Stack>
              )}
            </Box>

            <Divider />

            {/* Input Field */}
            <Box sx={{ p: 2 }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Type your message or use voice command..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={isSending || isListening}
                multiline
                maxRows={4}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Button 
                        color="primary" 
                        variant="contained" 
                        endIcon={<SendIcon />}
                        onClick={handleSendMessage}
                        disabled={!inputMessage.trim() || isSending || isListening}
                      >
                        Send
                      </Button>
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
          </Paper>
        </Stack>

        {/* Speed Dial for Quick Actions */}
        <SpeedDial
          ariaLabel="Quick Actions"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          icon={<SpeedDialIcon />}
        >
          {speedDialActions.map((action) => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipTitle={action.name}
              onClick={action.action}
            />
          ))}
        </SpeedDial>
      </Container>

      {/* Event Creation Dialog */}
      <EventCreationDialog
        open={showEventDialog}
        onClose={() => setShowEventDialog(false)}
        onSave={handleSaveEvent}
        defaultDate={selectedDate}
      />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}
