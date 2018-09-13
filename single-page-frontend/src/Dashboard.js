import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import Badge from '@material-ui/core/Badge';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import NotificationsIcon from '@material-ui/icons/Notifications';
import { mainListItems, secondaryListItems } from './listItems';
import SimpleLineChart from './SimpleLineChart';
import SimpleTable from './SimpleTable';
import Button from '@material-ui/core/Button';
import axios from 'axios';

const drawerWidth = 240;

var rootURL = ''

if (process.env.NODE_ENV == 'development') {
  rootURL='http://localhost:5000'
}

const styles = theme => ({
  root: {
    display: 'flex',
  },
  toolbar: {
    paddingRight: 24, // keep right padding when drawer closed
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginLeft: 12,
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    flexGrow: 1,
  },
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing.unit * 7,
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing.unit * 9,
    },
  },
  appBarSpacer: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    padding: theme.spacing.unit * 3,
    height: '100vh',
    overflow: 'auto',
  },
  chartContainer: {
    marginLeft: -22,
  },
  tableContainer: {
    height: 320,
  },
});

class Dashboard extends React.Component {
  state = {
    open: false,
    pumpStatus: [{'id': 1, 'name': 'Pump 1', 'status': 'ON', 'gph': 400}]
  };

  componentDidMount = () => {
    axios.get(rootURL + "/status", { crossdomain: true }).then(response => {
      this.setState({pumpStatus: response.data.pump_status.status})
    })
  }

  handleNewPump = (e) => {
    e.preventDefault()
    axios.post(rootURL + "/add_pump", {crossdomain: true}).then(response => {
      this.setState({pumpStatus: response.data})
    })
  }
  handleRequestConcurrent100 = (e) => {
    e.preventDefault()
    axios.post(rootURL + "/generate_requests", 
              {'concurrent': 10,
              'total': 100,
              'url': 'http://noder:5004/users'},
              {crossdomain: true}).then(response => {
                alert(response.data.traffic)
              })
  }

  handleRequestConcurrent200 = (e) => {
    e.preventDefault()
    axios.post(rootURL + "/generate_requests", 
              {'concurrent': 20,
              'total': 200,
              'url': 'http://noder:5004/users'},
              {crossdomain: true}).then(response => {
                alert(response.data.traffic)
              })
  }

  handleRequestConcurrent300 = (e) => {
    e.preventDefault()
    axios.post(rootURL + "/generate_requests", 
              {'concurrent': 30,
              'total': 300,
              'url': 'http://noder:5004/users'},
              {crossdomain: true}).then(response => {
                alert(response.data.traffic)
              })
  }
  
  handleDrawerOpen = () => {
    this.setState({ open: true });
  };

  handleDrawerClose = () => {
    this.setState({ open: false });
  };

  render() {
    const { classes } = this.props;

    return (
      <React.Fragment>
        <CssBaseline />
        <div className={classes.root}>
          <AppBar
            position="absolute"
            className={classNames(classes.appBar, this.state.open && classes.appBarShift)}
          >
            <Toolbar disableGutters={!this.state.open} className={classes.toolbar}>
              <IconButton
                color="inherit"
                aria-label="Open drawer"
                onClick={this.handleDrawerOpen}
                className={classNames(
                  classes.menuButton,
                  this.state.open && classes.menuButtonHidden,
                )}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="title" color="inherit" noWrap className={classes.title}>
                Dashboard
              </Typography>
              <IconButton color="inherit">
                <Badge>
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Toolbar>
          </AppBar>
          <Drawer
            variant="permanent"
            classes={{
              paper: classNames(classes.drawerPaper, !this.state.open && classes.drawerPaperClose),
            }}
            open={this.state.open}
          >
            <div className={classes.toolbarIcon}>
              <IconButton onClick={this.handleDrawerClose}>
                <ChevronLeftIcon />
              </IconButton>
            </div>
            <Divider />
            <List>{mainListItems}</List>
            <Divider />
            <List>{secondaryListItems}</List>
          </Drawer>
          <main className={classes.content}>
            <div className={classes.appBarSpacer} />
            <Typography variant="display1" gutterBottom>
              Water Demand 
            </Typography>
            <Typography component="div" className={classes.chartContainer}>
              <SimpleLineChart />
            </Typography>
            <Typography variant="display1" gutterBottom>
              Pump Status <Button style={{float: 'right'}} variant="contained" color="primary" onClick={this.handleNewPump}>
                Add Pump
              </Button>
            </Typography>
            <div className={classes.tableContainer}>
              <SimpleTable  pumps={this.state.pumpStatus}/>
            </div>
            <Typography variant="display1" gutterBottom>
              Generate Traffic
            </Typography>
            <p>
            <Button size="large" variant="contained" color="default" onClick={this.handleRequestConcurrent100}>
                100 users @ 10 concurrent requests
            </Button></p>
            <p><Button size="large" variant="contained" color="primary" onClick={this.handleRequestConcurrent200}>
                200 users @ 20 concurrent requests
            </Button></p>
            <p><Button size="large" variant="contained" color="secondary" onClick={this.handleRequestConcurrent300}>
                300 users @ 30 concurrent requests
            </Button></p>
          </main>
        </div>
      </React.Fragment>
    );
  }
}

Dashboard.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(styles)(Dashboard);
