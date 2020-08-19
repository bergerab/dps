import React, { useState } from 'react';
import { Link } from "react-router-dom";
import { withStyles } from '@material-ui/core/styles';

const styles = theme => ({
    link: {
        textDecoration: 'none',
        color: 'initial',
    },    
});

class MyLink extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const { classes } = this.props;        
        return (
            <Link className={classes.link} {...this.props} />
        );
    }
}

export default withStyles(styles, { withTheme: true })(MyLink);

